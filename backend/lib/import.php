<?php
include "/var/www/ug2_config.php";//

$db = mysqli_connect (null, THE_DB_USN, null, THE_DB_NAME, null, "/var/lib/mysql/mysql.sock") or die ("Could Not connect to Database Server.");
$db2 = mysqli_connect (null, THE_DB_USN, null, THE_DB_NAME, null, "/var/lib/mysql/mysql.sock") or die ("Could Not connect to Database Server.");

include "../api/model_k.php";
include "../api/model.php";
include "rest.php";
include "session.php";


function import_loc ()
{
	// $q = " select district_2019, county_2019, subcounty_2019, parish_2019, lc1_2019,  Region,  ec_constituency_2019  from ubos order by district_2019, county_2019, subcounty_2019, parish_2019, lc1_2019,  Region,  ec_constituency_2019";

	$q = "SELECT region, district_2019, county_2019, subcounty_2019, parish_2019, lc1_2019, ec_constituency_2019 FROM ugloc ORDER BY region, district_2019, county_2019, subcounty_2019, parish_2019, lc1_2019, ec_constituency_2019";

	$res = qryp ($q, "", [], 0);

	if ($res==NULL) return;
	
	$i = 0;
	$V = [null,null,null,null,null,null,null];
	$ID = ["88","0","0","0","0","0","0"];

	while ($row = mysqli_fetch_row ($res))
	{	
		for ($j=0; $j<7; $j++)
		{
			if ($V[$j]==$row[$j]) continue;
			$V[$j]=$row[$j];
			for ($k=$j+1; $k<7; $k++) { $V[$k]=null; $ID[($j+1)]="0"; }
			$p = [];
			$o = [];
			$o["category_id"] = $ID[$j];
			$o["name"] = $row[$j];

			$rt = rest_uri_post ("subcategories", NULL, $o, $p);
			if ($rt!=201) { error_log ("ERROR ".$rt."  row:".$i." col:".$j); continue; }
			
			$ID[($j+1)] = $p["subcategory_id"];
			// echo $V[$j]."\r\n";
		}
		$i++;
		// sleep (1);
	}
}

function import_case_categories ()
{
	$q = "SELECT F2, F3 FROM test.counselling ORDER BY  F1, F2, F3";

	$res = qryp ($q, "", [], 0);

	if ($res==NULL) return;
	
	$i = 0;
	$V = [null,null,null,null,null,null,null];
	$ID = ["361944","0","0","0","0","0","0"];

	while ($row = mysqli_fetch_row ($res))
	{	
		for ($j=0; $j<2; $j++)
		{
			if ($V[$j]==$row[$j]) continue;
			$V[$j]=$row[$j];
			for ($k=$j+1; $k<2; $k++) { $V[$k]=null; $ID[($j+1)]="0"; }
			$p = [];
			$o = [];
			$o["category_id"] = $ID[$j];
			$o["name"] = $row[$j];

			$rt = rest_uri_post ("subcategories", NULL, $o, $p);
			if ($rt!=201) { error_log ("ERROR ".$rt."  row:".$i." col:".$j); continue; }
			
			$ID[($j+1)] = $p["subcategory_id"];
			// echo $V[$j]."\r\n";
		}
		$i++;
		// sleep (1);
	}
}


function split_category ()
{
	$q = "SELECT id, case_category FROM kase";

	$res = qryp ($q, "", [], 0);
	
	while ($row = mysqli_fetch_row ($res))
	{
		$qu = "UPDATE kase SET cat_0=?, cat_1=?, cat_2=?, cat_3=?, cat_4=? WHERE id=?";
		$du = "ssssss";
		$av = ["","","","","",$row[0]];
		$vv = explode ('^',$row[1]);
		$n = count ($vv);
		for ($j=1; $j<$n; $j++) 
		{
			if ($j>5) break;
			$av[($j-1)] = $vv[$j];
		}
		qryp ($qu, $du, $av, 3, "db2");
	}
}

function autoexten ()
{
	$q = "select id, exten from auth where exten not like '000' order by exten";

	$res = qryp ($q, "", [], 0);
	
	while ($row = mysqli_fetch_row ($res))
	{
		$o = [];
		$p = [];
		$o["user_id"] = $row[0];
		$rt = rest_uri_post ("users", "", $o["user_id"], $o, $p); 
		if ($rt!=202) { echo "ERROR ".$rt."  user_id:".$o["user_id"]; continue; }
	}

}

// autoexten ();

// error_log (json_encode ($_SESSION));
// import_loc ();
// import_case_categories  ();
// split_category ();
?>
