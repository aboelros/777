FROM golang:1.23-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache git gcc musl-dev sqlite-dev

# Copy go mod files
COPY go.mod ./
RUN go get go.mau.fi/whatsmeow@v0.0.0-20240226093758-c9c0c3cfb8c3 && go mod download

# Copy source code
COPY . .

# Build
RUN CGO_ENABLED=1 go build -o gateway main.go

# Final stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates sqlite-libs

WORKDIR /root/

# Copy binary
COPY --from=builder /app/gateway .

# Create sessions directory
RUN mkdir -p sessions

# Expose port
EXPOSE 8080

# Run
CMD ["./gateway"]
