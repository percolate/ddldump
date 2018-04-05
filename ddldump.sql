-- Create syntax for TABLE 'alembic_version'
CREATE TABLE "alembic_version" (
    "version_num" character varying(32) NOT NULL
);
ALTER TABLE ONLY "public"."alembic_version" ADD CONSTRAINT "version_num_pkey" PRIMARY KEY ("version_num");
COMMENT ON COLUMN "alembic_version"."version_num" IS 'Migration Version number';
COMMENT ON TABLE "alembic_version" IS 'Track database migration versions.';

-- Create syntax for TABLE 'ddldump_test'
CREATE TABLE "ddldump_test" (
    "id" bigint NOT NULL,
    "name" character varying(255) NOT NULL,
    "type" character varying(64) NOT NULL,
    "parent_id" bigint,
    "big_chunk" "jsonb",
    "description" "text",
    "embiggened" boolean DEFAULT false,
    "updated_at" timestamp without time zone DEFAULT "now"(),
    "deleted_at" timestamp without time zone
);
ALTER TABLE ONLY "public"."ddldump_test" ADD CONSTRAINT "ddldump_test_pkey" PRIMARY KEY ("id");
ALTER TABLE ONLY "public"."ddldump_test" ADD CONSTRAINT "ddldump_test_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "ddldump_test"("id") ON DELETE CASCADE;
COMMENT ON COLUMN "ddldump_test"."id" IS 'Percoflake ID of the saved query folder.';
COMMENT ON COLUMN "ddldump_test"."name" IS 'Name of the saved query folder.';
COMMENT ON COLUMN "ddldump_test"."type" IS 'Type of the saved query folder as defined in apps.data.saved_query.constants.TYPES';
COMMENT ON COLUMN "ddldump_test"."updated_at" IS 'Time the saved query was last updated. NULL if not yet updated.';
CREATE INDEX "idx_ddldump_test_parent_id" ON "public"."ddldump_test" USING "btree" ("parent_id");
CREATE INDEX "idx_ddldump_test_type" ON "public"."ddldump_test" USING "btree" ("type");
