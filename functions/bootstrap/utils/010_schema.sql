CREATE EXTENSION postgis;
CREATE SCHEMA ofpnd;

GRANT USAGE ON SCHEMA ofpnd TO ${DB_SOLUTION_USER};

ALTER DEFAULT PRIVILEGES IN SCHEMA ofpnd GRANT SELECT ON TABLES TO ${DB_SOLUTION_USER};

ALTER DEFAULT PRIVILEGES IN SCHEMA ofpnd GRANT SELECT ON SEQUENCES TO ${DB_SOLUTION_USER};


CREATE TABLE ofpnd.floresta_publica_nao_destinada (
	codigo TEXT NOT NULL,
	nome text NOT null default 'Desconhecido',
	esfera text NOT NULL,
	orgao text NOT NULL,
	estagio text NOT NULL,
	estado text NOT NULL,
	ano integer NOT NULL,
	bioma text NOT NULL,
	geom geometry(multipolygon, 4674) NOT NULL,
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
	fpnd_area_ha float NOT NULL,
	carbono_estoque_ton float NOT NULL,
	carbono_densidade_ton_ha float NOT NULL,
	carbono_equivalencia_co2_ton_ha float NOT NULL,
	especie_diversidade_media float NOT NULL,
	car_sobreposicao_fpnd_ha float NOT NULL,
	car_sobreposicao_fpnd_per float NOT NULL,
	mineracao_area_ha float NOT NULL,
	floresta_original_area_ha float NOT NULL,
	floresta_atual_area_ha float NOT NULL,
	floresta_atual_area_per float NOT NULL,	
	desmatamento_area_ha float NOT NULL,
	desmatamento_area_per float NOT null,
	CONSTRAINT informacao_pkey PRIMARY KEY (codigo),
	CONSTRAINT floresta_publica_nao_destinada_fkey FOREIGN KEY (codigo) REFERENCES ofpnd.floresta_publica_nao_destinada(codigo) ON DELETE CASCADE ON UPDATE CASCADE
);


