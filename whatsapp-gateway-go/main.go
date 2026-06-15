package main

import (
	"context"
	"encoding/base64"
	"fmt"
	"log"
	"net/http"
	"os"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/skip2/go-qrcode"
	"go.mau.fi/whatsmeow"
	waProto "go.mau.fi/whatsmeow/binary/proto"
	"go.mau.fi/whatsmeow/store/sqlstore"
	"go.mau.fi/whatsmeow/types"
	"go.mau.fi/whatsmeow/types/events"
	waLog "go.mau.fi/whatsmeow/util/log"
)

type Session struct {
	ID           string                 `json:"id"`
	Client       *whatsmeow.Client      `json:"-"`
	QRCode       string                 `json:"qr_code,omitempty"`
	Status       string                 `json:"status"`
	CreatedAt    time.Time              `json:"created_at"`
	LastActivity time.Time              `json:"last_activity"`
	Metadata     map[string]interface{} `json:"metadata,omitempty"`
}

type SessionManager struct {
	sessions map[string]*Session
	mu       sync.RWMutex
	container *sqlstore.Container
	log      waLog.Logger
}

func NewSessionManager() (*SessionManager, error) {
	// Create sessions directory
	os.MkdirAll("./sessions", 0755)

	// Initialize database
	dbLog := waLog.Stdout("Database", "INFO", true)
	container, err := sqlstore.New("sqlite3", "file:./sessions/sessions.db?_foreign_keys=on", dbLog)
	if err != nil {
		return nil, fmt.Errorf("failed to create database: %w", err)
	}

	return &SessionManager{
		sessions:  make(map[string]*Session),
		container: container,
		log:       waLog.Stdout("SessionManager", "INFO", true),
	}, nil
}

func (sm *SessionManager) CreateSession(sessionID string, metadata map[string]interface{}) (*Session, error) {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	// Close existing session if any
	if existing, ok := sm.sessions[sessionID]; ok {
		sm.log.Infof("Session %s already exists, closing it", sessionID)
		if existing.Client != nil {
			existing.Client.Disconnect()
		}
		delete(sm.sessions, sessionID)
	}

	// Get device store
	deviceStore, err := sm.container.GetFirstDevice()
	if err != nil {
		return nil, fmt.Errorf("failed to get device: %w", err)
	}

	// Create WhatsApp client
	client := whatsmeow.NewClient(deviceStore, sm.log)

	session := &Session{
		ID:           sessionID,
		Client:       client,
		Status:       "connecting",
		CreatedAt:    time.Now(),
		LastActivity: time.Now(),
		Metadata:     metadata,
	}

	// Store session
	sm.sessions[sessionID] = session

	// Handle events
	client.AddEventHandler(func(evt interface{}) {
		switch v := evt.(type) {
		case *events.Connected:
			sm.log.Infof("Session %s connected", sessionID)
			session.Status = "connected"
			session.QRCode = ""
		case *events.Disconnected:
			sm.log.Infof("Session %s disconnected", sessionID)
			session.Status = "disconnected"
		case *events.LoggedOut:
			sm.log.Infof("Session %s logged out", sessionID)
			session.Status = "logged_out"
			sm.mu.Lock()
			delete(sm.sessions, sessionID)
			sm.mu.Unlock()
		}
	})

	// Generate QR code if not logged in
	if client.Store.ID == nil {
		qrChan, err := client.GetQRChannel(context.Background())
		if err != nil {
			return nil, fmt.Errorf("failed to get QR channel: %w", err)
		}

		// Connect
		err = client.Connect()
		if err != nil {
			return nil, fmt.Errorf("failed to connect: %w", err)
		}

		// Wait for QR code
		go func() {
			for evt := range qrChan {
				if evt.Event == "code" {
					// Generate QR code image
					png, err := qrcode.Encode(evt.Code, qrcode.Medium, 256)
					if err != nil {
						sm.log.Errorf("Failed to generate QR code: %v", err)
						continue
					}

					// Convert to base64
					qrBase64 := "data:image/png;base64," + base64.StdEncoding.EncodeToString(png)
					session.QRCode = qrBase64
					session.Status = "qr_ready"
					sm.log.Infof("QR code generated for session %s", sessionID)
				} else if evt.Event == "success" {
					sm.log.Infof("QR code scanned successfully for session %s", sessionID)
					session.Status = "connected"
					session.QRCode = ""
				} else if evt.Event == "timeout" {
					sm.log.Warnf("QR code timeout for session %s", sessionID)
					session.Status = "timeout"
				}
			}
		}()
	} else {
		// Already logged in, just connect
		err = client.Connect()
		if err != nil {
			return nil, fmt.Errorf("failed to connect: %w", err)
		}
		session.Status = "connected"
	}

	return session, nil
}

func (sm *SessionManager) GetSession(sessionID string) (*Session, bool) {
	sm.mu.RLock()
	defer sm.mu.RUnlock()
	session, ok := sm.sessions[sessionID]
	return session, ok
}

func (sm *SessionManager) CloseSession(sessionID string) error {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	session, ok := sm.sessions[sessionID]
	if !ok {
		return fmt.Errorf("session not found")
	}

	if session.Client != nil {
		session.Client.Disconnect()
	}

	delete(sm.sessions, sessionID)
	return nil
}

func (sm *SessionManager) SendMessage(sessionID, to, message string) error {
	session, ok := sm.GetSession(sessionID)
	if !ok {
		return fmt.Errorf("session not found")
	}

	if session.Status != "connected" {
		return fmt.Errorf("session not connected")
	}

	// Parse JID
	jid, err := parseJID(to)
	if err != nil {
		return fmt.Errorf("invalid phone number: %w", err)
	}

	// Send message
	_, err = session.Client.SendMessage(context.Background(), jid, &waProto.Message{
		Conversation: &message,
	})

	return err
}

func parseJID(phone string) (types.JID, error) {
	// Remove non-digits
	cleaned := ""
	for _, r := range phone {
		if r >= '0' && r <= '9' {
			cleaned += string(r)
		}
	}

	if cleaned == "" {
		return types.JID{}, fmt.Errorf("invalid phone number")
	}

	return types.NewJID(cleaned, types.DefaultUserServer), nil
}

func main() {
	// Initialize session manager
	sm, err := NewSessionManager()
	if err != nil {
		log.Fatalf("Failed to create session manager: %v", err)
	}

	// Create Gin router
	r := gin.Default()

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	// Create session
	r.POST("/sessions", func(c *gin.Context) {
		var req struct {
			SessionID string                 `json:"session_id"`
			Metadata  map[string]interface{} `json:"metadata"`
		}

		if err := c.BindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		session, err := sm.CreateSession(req.SessionID, req.Metadata)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, session)
	})

	// Get session status
	r.GET("/sessions/:sessionId/status", func(c *gin.Context) {
		sessionID := c.Param("sessionId")
		session, ok := sm.GetSession(sessionID)
		if !ok {
			c.JSON(http.StatusNotFound, gin.H{"error": "session not found"})
			return
		}

		c.JSON(http.StatusOK, session)
	})

	// Close session
	r.POST("/sessions/:sessionId/close", func(c *gin.Context) {
		sessionID := c.Param("sessionId")
		err := sm.CloseSession(sessionID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "closed"})
	})

	// Send message
	r.POST("/sessions/:sessionId/send", func(c *gin.Context) {
		sessionID := c.Param("sessionId")

		var req struct {
			To      string `json:"to"`
			Message string `json:"message"`
		}

		if err := c.BindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		err := sm.SendMessage(sessionID, req.To, req.Message)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "sent"})
	})

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("🚀 WhatsApp Gateway (whatsmeow) running on port %s", port)
	r.Run(":" + port)
}
