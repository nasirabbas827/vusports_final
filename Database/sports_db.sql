-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 28, 2026 at 09:08 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `sports_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `username`, `password`) VALUES
(1, 'admin', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `coaches`
--

CREATE TABLE `coaches` (
  `id` int(11) NOT NULL,
  `coach_name` varchar(100) NOT NULL,
  `profile_picture` varchar(255) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `specialization` varchar(100) DEFAULT NULL,
  `bio` text DEFAULT NULL,
  `sports_expertise` text DEFAULT NULL,
  `team_management` text DEFAULT NULL,
  `availability` varchar(100) DEFAULT NULL,
  `status` enum('pending','active','suspended') DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `coaches`
--

INSERT INTO `coaches` (`id`, `coach_name`, `profile_picture`, `email`, `password`, `specialization`, `bio`, `sports_expertise`, `team_management`, `availability`, `status`, `created_at`) VALUES
(1, 'NASIR ABBAS', 'uploads/1cccee61a7e645489f3e0757c1f90c44_service.jpg', 'nasiryt.827@gmail.com', '123', 'None', 'None', 'None', 'None', 'None', 'active', '2026-01-28 05:59:55'),
(2, 'Haider', NULL, 'haider@gmail.com', '123', NULL, 'xcz', NULL, NULL, NULL, 'active', '2026-01-28 06:00:54');

-- --------------------------------------------------------

--
-- Table structure for table `coach_sports`
--

CREATE TABLE `coach_sports` (
  `id` int(11) NOT NULL,
  `coach_id` int(11) NOT NULL,
  `sport_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `coach_sports`
--

INSERT INTO `coach_sports` (`id`, `coach_id`, `sport_id`) VALUES
(1, 1, 2),
(2, 2, 1);

-- --------------------------------------------------------

--
-- Table structure for table `participants`
--

CREATE TABLE `participants` (
  `id` int(11) NOT NULL,
  `vu_id` varchar(20) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `profile_picture` varchar(255) DEFAULT NULL,
  `bio` text DEFAULT NULL,
  `status` enum('pending','active','suspended') DEFAULT 'pending',
  `sports_preferences` text DEFAULT NULL,
  `past_participation` text DEFAULT NULL,
  `achievements` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `participants`
--

INSERT INTO `participants` (`id`, `vu_id`, `full_name`, `email`, `password`, `profile_picture`, `bio`, `status`, `sports_preferences`, `past_participation`, `achievements`, `created_at`) VALUES
(1, 'BC323232', 'Kainat Sofi', 'kainatsofi.8bp@gmail.com', '123', 'uploads/fb0857c176b549b996ba543721e10bb7_service.jpg', 'None', 'active', 'None', 'None', 'None', '2026-01-28 07:13:35');

-- --------------------------------------------------------

--
-- Table structure for table `participant_sport_requests`
--

CREATE TABLE `participant_sport_requests` (
  `id` int(11) NOT NULL,
  `participant_id` int(11) NOT NULL,
  `sport_id` int(11) NOT NULL,
  `coach_id` int(11) DEFAULT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `request_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `participant_sport_requests`
--

INSERT INTO `participant_sport_requests` (`id`, `participant_id`, `sport_id`, `coach_id`, `status`, `request_date`) VALUES
(1, 1, 2, 1, 'approved', '2026-01-28 07:13:35'),
(2, 1, 1, NULL, 'pending', '2026-01-28 07:13:35');

-- --------------------------------------------------------

--
-- Table structure for table `sports`
--

CREATE TABLE `sports` (
  `id` int(11) NOT NULL,
  `sport_name` varchar(50) NOT NULL,
  `description` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sports`
--

INSERT INTO `sports` (`id`, `sport_name`, `description`) VALUES
(1, 'Football', 'Team sport played between two teams of eleven players using a ball.'),
(2, 'Cricket', 'Bat-and-ball game played between two teams on a cricket field.'),
(3, 'Badminton', 'Racket sport played using a shuttlecock across a net.'),
(4, 'Basketball', 'Team sport where two teams try to score by shooting a ball through a hoop.'),
(5, 'Volleyball', 'Team sport where two teams hit a ball over a high net.'),
(6, 'Table Tennis', 'Indoor sport played by hitting a lightweight ball across a table using paddles.'),
(7, 'Tennis', 'Racket sport played individually or in doubles on a court.'),
(8, 'Hockey', 'Fast-paced team sport played with sticks and a ball or puck.'),
(9, 'Athletics', 'Collection of sporting events including running, jumping, and throwing.'),
(10, 'Swimming', 'Individual or team sport requiring movement through water using specific techniques.');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `coaches`
--
ALTER TABLE `coaches`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `coach_sports`
--
ALTER TABLE `coach_sports`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `sport_id` (`sport_id`),
  ADD KEY `coach_id` (`coach_id`);

--
-- Indexes for table `participants`
--
ALTER TABLE `participants`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `vu_id` (`vu_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `participant_sport_requests`
--
ALTER TABLE `participant_sport_requests`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `participant_id` (`participant_id`,`sport_id`),
  ADD KEY `sport_id` (`sport_id`),
  ADD KEY `coach_id` (`coach_id`);

--
-- Indexes for table `sports`
--
ALTER TABLE `sports`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `sport_name` (`sport_name`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `coaches`
--
ALTER TABLE `coaches`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `coach_sports`
--
ALTER TABLE `coach_sports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `participants`
--
ALTER TABLE `participants`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `participant_sport_requests`
--
ALTER TABLE `participant_sport_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `sports`
--
ALTER TABLE `sports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `coach_sports`
--
ALTER TABLE `coach_sports`
  ADD CONSTRAINT `coach_sports_ibfk_1` FOREIGN KEY (`coach_id`) REFERENCES `coaches` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `coach_sports_ibfk_2` FOREIGN KEY (`sport_id`) REFERENCES `sports` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `participant_sport_requests`
--
ALTER TABLE `participant_sport_requests`
  ADD CONSTRAINT `participant_sport_requests_ibfk_1` FOREIGN KEY (`participant_id`) REFERENCES `participants` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `participant_sport_requests_ibfk_2` FOREIGN KEY (`sport_id`) REFERENCES `sports` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `participant_sport_requests_ibfk_3` FOREIGN KEY (`coach_id`) REFERENCES `coaches` (`id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
