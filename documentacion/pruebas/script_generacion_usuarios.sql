DO $$
BEGIN
FOR r IN 200..300
	LOOP
		INSERT INTO public."USUARIO"(
		nombre, apellidos, login, password, estado, "idEmpresa", "idJornadaLaboral", "idRol", "idUsuario", nif, "emailRecuperacion", imei, tlf)
		VALUES ('nombre', 'apellidos', concat(cast(r as varchar), '@prueba.es'),'pbkdf2:sha256:260000$QcMI34xIgoRCz3LN$42fc5a0aa3249d7db64e0293b49462ee671b8a11bc526d7e75381d1098349021', True, 26, 1, 0, r, '12345678Y', 'prueba@prueba.es', '121212', '981121212');
	END LOOP;
END $$;