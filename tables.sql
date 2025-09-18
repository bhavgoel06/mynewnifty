CREATE TABLE `fake_zeroda_orders` (
  `order_id` int NOT NULL AUTO_INCREMENT,
  `tradingsymbol` varchar(45) DEFAULT NULL,
  `quantity` decimal(18,2) DEFAULT NULL,
  `exchange` varchar(45) DEFAULT NULL,
  `transaction_type` varchar(45) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `product` varchar(45) DEFAULT NULL,
  `order_type` varchar(45) DEFAULT NULL,
  `price` decimal(18,2) DEFAULT NULL,
  `stop_loss_trigger_price` decimal(18,2) DEFAULT NULL,
  `status` varchar(45) DEFAULT NULL,
  `intent` varchar(45) DEFAULT 'Fresh',
  `userid` varchar(45) DEFAULT NULL,
  `StopLossStatus` varchar(45) DEFAULT 'None',
  `remarks` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `fake_zeroda_trades` (
  `trade_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int DEFAULT NULL,
  `exchange` varchar(45) DEFAULT NULL,
  `tradingsymbol` varchar(45) DEFAULT NULL,
  `average_price` decimal(18,2) DEFAULT NULL,
  `quantity` int DEFAULT NULL,
  `transaction_type` varchar(45) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `brokerage` int DEFAULT '90',
  `trade_date` date DEFAULT NULL,
  PRIMARY KEY (`trade_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `fake_zeroda_positions` (
  `tradingsymbol` varchar(45) DEFAULT NULL,
  `exchange` varchar(45) DEFAULT NULL,
  `product` varchar(45) DEFAULT NULL,
  `quantity` int DEFAULT NULL,
  `average_price` decimal(18,2) DEFAULT NULL,
  `last_price` decimal(18,2) DEFAULT NULL,
  `m2m` decimal(18,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


