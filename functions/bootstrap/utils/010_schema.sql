CREATE EXTENSION postgis;
CREATE SCHEMA ofpnd;

GRANT USAGE ON SCHEMA ofpnd TO ${DB_SOLUTION_USER};

ALTER DEFAULT PRIVILEGES IN SCHEMA ofpnd GRANT SELECT ON TABLES TO ${DB_SOLUTION_USER};

ALTER DEFAULT PRIVILEGES IN SCHEMA ofpnd GRANT SELECT ON SEQUENCES TO ${DB_SOLUTION_USER};


CREATE TABLE ofpnd.floresta_publica_nao_destinada (
	codigo text NOT NULL,
	nome text DEFAULT 'Desconhecido'::text NOT NULL,
	esfera text NOT NULL,
	orgao text NOT NULL,
	estagio text NOT NULL,
	estado text NOT NULL,
	ano int4 NOT NULL,
	bioma text NOT NULL,
	geom public.geometry(multipolygon, 4674) NOT NULL,
	uf text NULL,
	CONSTRAINT floresta_publica_nao_destinada_pkey PRIMARY KEY (codigo)
);

CREATE TABLE ofpnd.desmatamento (
	codigo text NOT NULL,
	data date NOT null,
	fonte text NOT NULL,
    area_ha float NOT NULL,
	CONSTRAINT desmatamento_pkey PRIMARY KEY (codigo, data, fonte),
	CONSTRAINT floresta_publica_nao_destinada_fkey FOREIGN KEY (codigo) REFERENCES ofpnd.floresta_publica_nao_destinada(codigo) ON DELETE CASCADE ON UPDATE CASCADE
);

--drop TABLE ofpnd.informacao ;

CREATE TABLE ofpnd.informacao (
	codigo text NOT NULL,
	fpnd_area_ha float8 NOT NULL,
	carbono_estoque_ton float8 NOT NULL,
	carbono_densidade_ton_ha float8 NOT NULL,
	carbono_equivalencia_co2_ton_ha float8 NOT NULL,
	especie_diversidade_media float8 NOT NULL,
	car_sobreposicao_fpnd_ha float8 NOT NULL,
	car_sobreposicao_fpnd_per float8 NOT NULL,
	mineracao_area_ha float8 NOT NULL,
	floresta_original_area_ha float8 NOT NULL,
	floresta_atual_area_ha float8 NOT NULL,
	floresta_atual_area_per float8 NOT NULL,
	desmatamento_area_ha float8 NOT NULL,
	desmatamento_area_per float8 NOT NULL,
	CONSTRAINT informacao_pkey PRIMARY KEY (codigo),
	CONSTRAINT floresta_publica_nao_destinada_fkey FOREIGN KEY (codigo) REFERENCES ofpnd.floresta_publica_nao_destinada(codigo) ON DELETE CASCADE ON UPDATE CASCADE
);


