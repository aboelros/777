BEGIN;

-- Running upgrade c1412562210a -> b7d41f09e2a1

CREATE TABLE business_context (
    id UUID NOT NULL, 
    project_id UUID NOT NULL, 
    context_type VARCHAR(100) NOT NULL, 
    context_key VARCHAR(255) NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    content TEXT NOT NULL, 
    tags JSONB DEFAULT '[]'::jsonb, 
    relevance_score FLOAT DEFAULT 1.0, 
    times_used INTEGER DEFAULT 0, 
    learned_from VARCHAR(100), 
    confidence_score FLOAT DEFAULT 0.5, 
    active_for_platforms JSONB DEFAULT '[]'::jsonb, 
    examples JSONB DEFAULT '[]'::jsonb, 
    is_active BOOLEAN DEFAULT true, 
    last_used TIMESTAMP WITH TIME ZONE, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE
);

CREATE INDEX idx_business_context_project ON business_context (project_id);

CREATE INDEX idx_business_context_type ON business_context (context_type);

CREATE INDEX idx_business_context_key ON business_context (context_key);

CREATE INDEX idx_business_context_used ON business_context (times_used);

ALTER TABLE business_context ENABLE ROW LEVEL SECURITY;

UPDATE alembic_version SET version_num='b7d41f09e2a1' WHERE alembic_version.version_num = 'c1412562210a';

-- Running upgrade b7d41f09e2a1 -> d8f3a1e5c2b4

CREATE TABLE product_images (
    key VARCHAR(500) NOT NULL, 
    project_id UUID, 
    data BYTEA NOT NULL, 
    content_type VARCHAR(100) NOT NULL, 
    size INTEGER NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (key), 
    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE
);

CREATE INDEX idx_product_images_project_id ON product_images (project_id);

ALTER TABLE product_images ENABLE ROW LEVEL SECURITY;

UPDATE alembic_version SET version_num='d8f3a1e5c2b4' WHERE alembic_version.version_num = 'b7d41f09e2a1';

COMMIT;

