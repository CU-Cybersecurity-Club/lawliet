--
-- Initialize database for VNC connections
--

-- Create connection
INSERT INTO guacamole_connection (connection_name, protocol)
    VALUES ("vnc-test", "vnc");
SET @id = LAST_INSERT_ID();

-- Add parameters
INSERT INTO guacamole_connection_parameter
    VALUES (@id, "hostname", "lawliet-vnc");
INSERT INTO guacamole_connection_parameter
    VALUES (@id, "port", "5901");
INSERT INTO guacamole_connection_parameter
    VALUES (@id, "password", "vncpass");


--
-- Initialize database for SSH connections
--
INSERT INTO guacamole_connection (connection_name, protocol)
    VALUES ("ssh-test", "ssh");
SET @id = LAST_INSERT_ID();

INSERT INTO guacamole_connection_parameter
    VALUES (@id, "hostname", "lawliet-ssh");
INSERT INTO guacamole_connection_parameter
    VALUES (@id, "port", "22");
