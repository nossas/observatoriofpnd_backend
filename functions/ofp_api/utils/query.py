DQ_GEO_FPND_AS_MVT = """
    WITH bounds AS
    (
        SELECT ST_TileEnvelope(${z},${x},${y}) value
    ),
    mvtgeom AS
    (
    SELECT ST_AsMVTGeom(st_transform(geom,3857), b.value, 1024, 256, true) AS geom, codigo, nome, esfera, uf, estado
    FROM 
        ofpnd.floresta_publica_nao_destinada INNER JOIN 
        bounds as b ON geom && st_transform(b.value,4326)
    )
    SELECT ST_AsMVT(mvtgeom.*,'fpnd',1024) as mvt
    FROM mvtgeom where geom is not null;
"""


DQ_MAP_DATA_LAST_MONTH = """
    set lc_time  TO 'pt_BR.UTF-8';
    SELECT
        TO_CHAR(max("data"),'TMMonth') "month"
    FROM
        ofpnd.desmatamento;        
"""

DQ_MAP_DATA_DEFORESTATION_LAST_MONTH = """
    WITH base AS (
        SELECT
            max("data") data
        FROM
            ofpnd.desmatamento
    )
    SELECT
        d.codigo geocode,
        d.area_ha deforastation_last_month
    FROM
        ofpnd.desmatamento d INNER join 
        base b 
        on
            d."data" = b.data
        order by
            d.area_ha desc;      
"""

DQ_MAP_DATA_DEFORESTATION_LAST_10_YEARS = """
    SELECT
        codigo,
        SUM(area_ha) AS deforastation_last_10_years
    FROM
        ofpnd.desmatamento
    WHERE
        "data" >= current_date - INTERVAL '10 years'
    GROUP BY
        codigo
    ORDER BY
        deforastation_last_10_years DESC;
"""

DQ_MAP_DATA = """
      SELECT
		codigo geocode,
		desmatamento_area_ha land_cover,
		carbono_densidade_ton_ha underground_carbon_storage,
		especie_diversidade_media species_diversity,
        car_sobreposicao_fpnd_per*100.0 car_overlap,
		mineracao_area_ha mining
	  FROM
		ofpnd.informacao;
"""

DQ_ENTENDA_INFORMACAO = """
SELECT
	i.codigo,
	esfera,
	fpnd_area_ha,
	carbono_estoque_ton,
	carbono_densidade_ton_ha,
	carbono_equivalencia_co2_ton_ha,
	especie_diversidade_media,
	car_sobreposicao_fpnd_ha,
	mineracao_area_ha,
	floresta_original_area_ha,
	floresta_atual_area_ha,
	desmatamento_area_ha
FROM
	ofpnd.informacao i INNER JOIN ofpnd.floresta_publica_nao_destinada fpnd ON i.codigo = fpnd.codigo
${where_clause};
"""

DQ_ENTENDA_DESMATAMENTO = """
select
	d.codigo,
	"data",
	fonte,
	area_ha
from
	ofpnd.desmatamento d inner join 
	ofpnd.floresta_publica_nao_destinada fpnd on d.codigo = fpnd.codigo
${where_clause};
"""