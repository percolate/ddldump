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
ALTER TABLE ONLY "public"."custom_record" ADD CONSTRAINT "custom_record_record_fkey" FOREIGN KEY ("id") REFERENCES "public"."record"("id") ON DELETE CASCADE;
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
    "big_chunk" "jsonb",
    "description" "text",
    "embiggened" boolean DEFAULT false,
    "updated_at" timestamp without time zone DEFAULT "now"(),
    "deleted_at" timestamp without time zone
);
ALTER TABLE ONLY "public"."record" ADD CONSTRAINT "record_pkey" PRIMARY KEY ("id");
ALTER TABLE ONLY "public"."record" ADD CONSTRAINT "record_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "public"."record"("id") ON DELETE CASCADE;
COMMENT ON COLUMN "public"."record"."id" IS 'Percoflake ID of the saved query folder.';
COMMENT ON COLUMN "public"."record"."name" IS 'Name of the saved query folder.';
COMMENT ON COLUMN "public"."record"."type" IS 'Type of the saved query folder as defined in apps.data.saved_query.constants.TYPES';
COMMENT ON COLUMN "public"."record"."updated_at" IS 'Time the saved query was last updated. NULL if not yet updated.';
CREATE INDEX "idx_record_parent_id" ON "public"."record" USING "btree" ("parent_id");
CREATE INDEX "idx_record_type" ON "public"."record" USING "btree" ("type");
SELECT pg_catalog.set_config('search_path', '', false);

CREATE OR REPLACE FUNCTION public.now_utc() RETURNS timestamp AS $$
  SELECT now() AT time zone 'utc';
  $$ LANGUAGE sql;

CREATE OR REPLACE FUNCTION public.trigger_set_timestamp()
  RETURNS TRIGGER
  LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = now_utc();
  RETURN NEW;
END;
$$;

COMMENT ON FUNCTION public.trigger_set_timestamp() IS 'Trigger function to update updated_at column on update';

DROP TRIGGER IF EXISTS update_timestamp on public.custom_record;

CREATE TRIGGER update_timestamp
  BEFORE UPDATE
  ON public.custom_record
  FOR EACH ROW
  EXECUTE PROCEDURE public.trigger_set_timestamp();

CREATE OR REPLACE VIEW public.custom_record_view AS (
  SELECT
    c.id,
    r.id as subject_id
  FROM
    public.custom_record c
    INNER JOIN public.record r ON c.id = r.id
  WHERE
    r.type IN ('new', 'in_progress', 'complete')
    AND c.deleted_at IS NULL
);


