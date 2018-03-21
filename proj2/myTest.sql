USE test;
DROP TABLE auto;
CREATE TABLE auto (pid int, name varchar(20), price float);
--;
insert into auto values(1, 'Gizmo', 19.99);
INSERT INTO auto values(2, 'PowerGizmo', 29.99);
INSERT INTO auto values(3, 'SingleTouch', 149.99);
INSERT INTO auto values(4, 'MultiTouch', 199.99);
INSERT INTO auto values(5, 'SuperGizmo', 49.99);
--;
SELECT * FROM auto
WHERE price > 150;
--;
SELECT pid, price FROM auto
WHERE price > 150;
--; 
UPDATE auto
SET name = 'Gizmo'
WHERE name = 'SuperGizmo';
--;
SELECT pid, name FROM auto;
--;
DELETE FROM auto 
WHERE name = "Gizmo";
--;
SELECT * FROM auto
WHERE price > 150;
--;
DELETE FROM auto 
WHERE price > 150;
--;
SELECT * FROM auto;
--;
.EXIT;
