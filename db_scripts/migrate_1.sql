-- GÂCHETTES

-- UNE GÂCHETTE SUR LA TABLE CATEGORIE POUR S'ASSURER QU'IL EXISTE UN SEUL PARENT RACINE
-- POUR TOUTE LA HIÉRARCHIE DE CATÉGORIE. LE PARENT EST LE SEUL TUPLE QUI POSSÈDE LA VALEUR "NULL"
-- POUR L'ID
CREATE TRIGGER uneSeuleRacineHierarchique
BEFORE INSERT ON categories
FOR EACH ROW
BEGIN
DECLARE nombreDeRacine INT;
DECLARE errorMsg TEXT;
    IF NEW.idCategorieParent IS NULL THEN
        SELECT COUNT(*) INTO nombreDeRacine FROM categories WHERE idCategorieParent IS NULL;
        IF nombreDeRacine > 0 THEN
            SET errorMsg = CONCAT('Il ne peut y avoir qu une seule categorie racine. La nouvelle categorie : ', NEW.nom,  ' doit avoir un parent');
           SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = errorMsg;
        END IF;
    END IF;
END ;
