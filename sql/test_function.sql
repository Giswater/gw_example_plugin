CREATE OR REPLACE FUNCTION test_function() RETURNS integer LANGUAGE plpgsql AS $function$
DECLARE
BEGIN
	RETURN 0;
END;
$function$;

