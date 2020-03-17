-- Create syntax for TABLE 'alembic_version'
CREATE TABLE "public"."alembic_version" (
    "version_num" character varying(32) NOT NULL
);
ALTER TABLE ONLY "public"."alembic_version" ADD CONSTRAINT "version_num_pkey" PRIMARY KEY ("version_num");
COMMENT ON COLUMN "public"."alembic_version"."version_num" IS 'Migration Version number';
COMMENT ON TABLE "public"."alembic_version" IS 'Track database migration versions.';
SELECT pg_catalog.set_config('search_path', '', false);

-- Create syntax for TABLE 'custom_record'
CREATE TABLE "public"."custom_record" (
    "id" bigint NOT NULL,
    "name" character varying(255) NOT NULL,
    "updated_at" timestamp without time zone DEFAULT "now"(),
    "deleted_at" timestamp without time zone
);
ALTER TABLE ONLY "public"."custom_record" ADD CONSTRAINT "custom_record_pkey" PRIMARY KEY ("id");
COMMENT ON COLUMN "public"."custom_record"."id" IS 'ID of the custom record.';
COMMENT ON COLUMN "public"."custom_record"."name" IS 'Name of the custom record.';
COMMENT ON COLUMN "public"."custom_record"."updated_at" IS 'Time the saved query was last updated. Null if not yet updated.';
CREATE INDEX "idx_custom_record_updated_at" ON "public"."custom_record" USING "btree" ("updated_at");
SELECT pg_catalog.set_config('search_path', '', false);

-- Create syntax for TABLE 'record'
CREATE TABLE "public"."record" (
    "id" bigint NOT NULL,
    "name" character varying(255) NOT NULL,
    "type" character varying(64) NOT NULL,
    "parent_id" bigint,
    "chunk_id" bigint NOT NULL,
    "big_chunk" "jsonb",
    "description" "text",
    "embiggened" boolean DEFAULT false,
    "updated_at" timestamp without time zone DEFAULT "now"(),
    "deleted_at" timestamp without time zone
);
CREATE SEQUENCE "public"."record_chunk_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
CREATE SEQUENCE "public"."record_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE ONLY "public"."record" ADD CONSTRAINT "record_pkey" PRIMARY KEY ("id");
ALTER SEQUENCE "public"."record_chunk_id_seq" OWNED BY "public"."record"."chunk_id";
ALTER SEQUENCE "public"."record_id_seq" OWNED BY "public"."record"."id";
ALTER TABLE ONLY "public"."record" ADD CONSTRAINT "record_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "public"."record"("id") ON DELETE CASCADE;
ALTER TABLE ONLY "public"."record" ALTER COLUMN "chunk_id" SET DEFAULT "nextval"('"public"."record_chunk_id_seq"'::"regclass");
ALTER TABLE ONLY "public"."record" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."record_id_seq"'::"regclass");
COMMENT ON COLUMN "public"."record"."id" IS 'Percoflake ID of the saved query folder.';
COMMENT ON COLUMN "public"."record"."name" IS 'Name of the saved query folder.';
COMMENT ON COLUMN "public"."record"."type" IS 'Type of the saved query folder as defined in apps.data.saved_query.constants.TYPES';
COMMENT ON COLUMN "public"."record"."updated_at" IS 'Time the saved query was last updated. NULL if not yet updated.';
CREATE INDEX "idx_record_parent_id" ON "public"."record" USING "btree" ("parent_id");
CREATE INDEX "idx_record_type" ON "public"."record" USING "btree" ("type");
SELECT pg_catalog.set_config('search_path', '', false);

-- Create syntax for TABLE 'custom_record_view'
SELECT pg_catalog.set_config('search_path', '', false);
CREATE VIEW "public"."custom_record_view" AS
 SELECT "c"."id",
    "r"."id" AS "subject_id"
   FROM ("public"."custom_record" "c"
     JOIN "public"."record" "r" ON (("c"."id" = "r"."id")))
  WHERE ((("r"."type")::"text" = ANY (ARRAY[('new'::character varying)::"text", ('in_progress'::character varying)::"text", ('complete'::character varying)::"text"])) AND ("c"."deleted_at" IS NULL));
