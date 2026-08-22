-- =============================================================================
-- OEIL DE DIEU v1.0 - Schema de base de donnees
-- NAG NAT Industries - 2026
-- =============================================================================
-- SGBD cible  : SQLite (via SQLAlchemy)
-- Charset     : UTF-8
-- Remarque    : Ce fichier est le schema de reference pour la documentation.
--               La creation effective des tables est geree par SQLAlchemy
--               (voir modules/base_donnees/base_donnees.py -> BaseDonnees.initialiser())
-- =============================================================================

PRAGMA journal_mode = WAL;   -- Meilleure concurrence en lecture
PRAGMA foreign_keys = ON;    -- Activer les cles etrangeres

-- ---------------------------------------------------------------------------
-- Table : personnes_recherchees
-- Fiches des personnes faisant l'objet d'une recherche active.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS personnes_recherchees (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    nom                  TEXT NOT NULL DEFAULT '',
    prenom               TEXT NOT NULL DEFAULT '',
    alias                TEXT DEFAULT '',
    description          TEXT DEFAULT '',
    statut               TEXT DEFAULT 'active'  -- active | suspendue | cloturee
                             CHECK (statut IN ('active', 'suspendue', 'cloturee')),
    chemin_photo         TEXT,          -- Chemin absolu ou relatif vers la photo de reference
    derniere_localisation TEXT,
    coordonnees_gps      TEXT,          -- Format : 'lat,lon'
    tags                 TEXT DEFAULT '',  -- JSON serialise : ["tag1", "tag2"]
    date_creation        TEXT NOT NULL DEFAULT (datetime('now')),
    date_mise_a_jour     TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Mise a jour automatique de date_mise_a_jour
CREATE TRIGGER IF NOT EXISTS trg_personnes_mise_a_jour
AFTER UPDATE ON personnes_recherchees
BEGIN
    UPDATE personnes_recherchees
    SET date_mise_a_jour = datetime('now')
    WHERE id = NEW.id;
END;

-- Index pour accelerer les recherches par statut
CREATE INDEX IF NOT EXISTS idx_personnes_statut
    ON personnes_recherchees (statut);

-- Index pour la recherche textuelle
CREATE INDEX IF NOT EXISTS idx_personnes_nom
    ON personnes_recherchees (nom, prenom);


-- ---------------------------------------------------------------------------
-- Table : evenements_surveillance
-- Evenements detectes par le systeme de surveillance.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS evenements_surveillance (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    type_evenement  TEXT NOT NULL  -- 'detection_faciale' | 'mouvement' | 'alerte' | 'info'
                        CHECK (type_evenement IN ('detection_faciale', 'mouvement', 'alerte', 'info')),
    source          TEXT DEFAULT '',   -- Identifiant de la camera / capteur
    description     TEXT DEFAULT '',
    confiance       REAL,              -- Score de confiance 0.0 - 1.0
    personne_id     INTEGER,           -- FK vers personnes_recherchees.id (nullable)
    horodatage      TEXT NOT NULL DEFAULT (datetime('now')),
    traite          INTEGER NOT NULL DEFAULT 0  -- 0 = non traite, 1 = traite
                        CHECK (traite IN (0, 1)),
    FOREIGN KEY (personne_id) REFERENCES personnes_recherchees (id)
        ON DELETE SET NULL
);

-- Index pour lister les evenements non traites
CREATE INDEX IF NOT EXISTS idx_evenements_traite
    ON evenements_surveillance (traite, horodatage DESC);

-- Index pour filtrer par personne
CREATE INDEX IF NOT EXISTS idx_evenements_personne
    ON evenements_surveillance (personne_id);


-- ---------------------------------------------------------------------------
-- Table : sessions_operateurs
-- Complement SQL des logs JSON (redondance securisee).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions_operateurs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    id_operateur    TEXT NOT NULL,
    nom             TEXT NOT NULL,
    prenom          TEXT NOT NULL,
    horodatage      TEXT NOT NULL DEFAULT (datetime('now')),
    adresse_ip      TEXT DEFAULT '',   -- Optionnel : IP de connexion
    signature_hmac  TEXT DEFAULT ''    -- HMAC-SHA256 pour integrite
);

CREATE INDEX IF NOT EXISTS idx_sessions_operateur
    ON sessions_operateurs (id_operateur, horodatage DESC);
