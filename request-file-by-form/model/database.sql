-- To enable UUID generate  support

CREATE EXTENSION pgcrypto;

-- Table: public."user"

-- DROP TABLE public."user";

CREATE TABLE public."user"
(
  id serial,
  name character varying(255) NOT NULL,
  email character varying(255) NOT NULL,
  institution character varying(255) NOT NULL,
  CONSTRAINT user_id_pk PRIMARY KEY (id),
  CONSTRAINT email_constraint UNIQUE (email)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public."user"
  OWNER TO postgres;

-- Table: public.downloads_by_uuid

-- DROP TABLE public.downloads_by_uuid;

CREATE TABLE public.downloads_by_uuid
(
  id serial,
  uuid uuid NOT NULL,
  num_downloads integer NOT NULL DEFAULT 0,
  user_id integer NOT NULL,
  CONSTRAINT download_by_uuid_pk PRIMARY KEY (id),
  CONSTRAINT user_fk FOREIGN KEY (user_id)
      REFERENCES public."user" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.downloads_by_uuid
  OWNER TO postgres;

-- Index: public.fki_user_fk

-- DROP INDEX public.fki_user_fk;

CREATE INDEX fki_user_fk
  ON public.downloads_by_uuid
  USING btree
  (user_id);

-- Table: public.request_by_ip

-- DROP TABLE public.request_by_ip;

CREATE TABLE public.request_by_ip
(
  id serial,
  id_download integer,
  ip character varying(255),
  CONSTRAINT request_by_ip_pk PRIMARY KEY (id),
  CONSTRAINT download_by_uuid_fk FOREIGN KEY (id_download)
      REFERENCES public.downloads_by_uuid (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.request_by_ip
  OWNER TO postgres;

-- Index: public.fki_download_by_uuid_fk

-- DROP INDEX public.fki_download_by_uuid_fk;

CREATE INDEX fki_download_by_uuid_fk
  ON public.request_by_ip
  USING btree
  (id_download);