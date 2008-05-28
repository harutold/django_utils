CREATE OR REPLACE FUNCTION {{ model_name }}_{{ action }}_handle() RETURNS trigger AS
$BODY$
{{ code|safe }}
$BODY$
LANGUAGE 'plpgsql' VOLATILE;

CREATE TRIGGER {{ action }}_handle
AFTER {{ event }}
ON {{ table_name }}
FOR EACH ROW
EXECUTE PROCEDURE {{ model_name }}_{{ action }}_handle();