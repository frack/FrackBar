-- FRACK CONSUMPTION DATABASE


-- Contains all products for sale
CREATE TABLE `product` (
  `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
  `barcode` VARCHAR,
  `name` VARCHAR,
  `memberprice` DECIMAL,
  `visitorprice` DECIMAL
);

-- Contains all sales
CREATE TABLE `sales` (
  `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
  `datetime` DATETIME,
  `product` INTEGER, -- refs `product`.`ID`
  `card` INTEGER, -- refs `creditcard`.`ID` ; Leave emtpy for no card.
  `member` BOOL
);

-- Contains all creditcards
CREATE TABLE `creditcard` (
  `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
  `datetime` DATETIME,
  `barcode` VARCHAR,
  `member` BOOL,
  `credit` DECIMAL
);

