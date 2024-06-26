CREATE TABLE urls (
    id BIGSERIAL PRIMARY KEY,
    original_url VARCHAR NOT NULL,
    short_key VARCHAR UNIQUE NOT NULL,
    created_at DATE DEFAULT CURRENT_DATE,
    expires_at DATE DEFAULT CURRENT_DATE + INTERVAL '30 days',
    access_count INTEGER DEFAULT 0
);

CREATE INDEX idx_urls_id ON urls (id);
CREATE INDEX idx_urls_short_key ON urls (short_key);