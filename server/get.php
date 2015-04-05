<?php
if (preg_match("/^[0-9]{10}\;[0-9]{1,5}\.?[0-9]{0,20}/", $_POST['val'])) {
	$val = explode(";", $_POST['val']);
	$updator = new RRDUpdater("power.rrd");
	$updator->update(array("power" => $val[1]), $val[0]);
	$fileh = fopen("power.log", "w+");
	fwrite($fileh, $_POST['val']);
	fclose($fileh);
	echo "0";
} else {
	echo "1";
}
?>

