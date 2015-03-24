<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <title>Stromverbrauch HQ</title>
    <link rel="icon" type="image/png" href="/png.ico">
<?php if (! isset($_GET['norefresh']) || $_GET['norefresh'] != 1): ?>
	<meta http-equiv="refresh" content="15">
<?php endif; ?>
	<style type="text/css">
		body {
			font-family: arial, sans-serif;
			font-size: 14px;
			color: #000;
			background-color: #eee;
		}
		dt {
			font-weight: bold;
			display: inline;
			float: left;
			margin: 0 0 0.3em 0;
			width: 100px;
		}
		dd {
			display: inline;
			float: left;
			margin: 0 0.5em 0 0;
		}
		dl dd + dt, dl dd + dd {
			clear: left;
		}
	</style>

		
</head>
<body>
	<h1>Aktueller Stromverbrauch im HQ</h1>
<?php
	$last = file_get_contents("power.log");
	$last = explode(";", $last);
	$power= $last[1];
	$time = date("H:i:s",$last[0]);
?>
	<dl>
		<dt>Zeitpunkt:</dt>
		<dd>
			<?= $time ?> 
			<?php if ($_GET['norefresh'] == 1): ?>
				[Neuladen: <a href="?norefresh=0">aktivieren</a>]
			<?php else: ?>
				[Neuladen: <a href="?norefresh=1">deaktivieren</a>]
			<?php endif; ?>
		</dd>
		<dt>Leistung:</dt>
		<dd><?= $power ?> Watt</dd>

	</dl>
	<br clear="both">
	<br>
	<strong>Plot der letzten Stunde</strong><br>
	<img src="power.png" alt="Leistung geplottet über die Zeit" border="0"><br>
	<strong>Plot der letzten 12 Stunden</strong><br>
	<img src="power12.png" alt="Leistung geplottet über die Zeit" border="0"><br>
	<strong>Plot der letzten 24 Stunden</strong><br>
	<img src="power24.png" alt="Leistung geplottet über die Zeit" border="0"><br>
	<strong>Plot der letzten Woche</strong><br>
	<img src="power1w.png" alt="Leistung geplottet über die Zeit" border="0"><br>
	<strong>Plot des letzten Monats</strong><br>
	<img src="power1m.png" alt="Leistung geplottet über die Zeit" border="0"><br>
	<strong>Plot des letzten Quartals</strong><br>
	<img src="power1q.png" alt="Leistung geplottet über die Zeit" border="0"><br>
	<strong>Plot des letzten Jahres</strong><br>
	<img src="power1y.png" alt="Leistung geplottet über die Zeit" border="0"><br>
</body>
</html>
