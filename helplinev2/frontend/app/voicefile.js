
te["vfile_moh_new"] = { div:["g","va"], s:["ba mtn1",""], c:
[ 
	{ input:["g","moh_new-vfiles","file[]","","file"], ev:["","_file_upload"] }, 
	{ s:["c xx y07 gw cb",""] },
	{ ac:["d x y02","","_rm","x y n","&Cross;"] },
	{ p:["d x y02","nb"], s:["x y go cw","Uploading ..."] }, // todo: show progress
	{ div:["e"] },
]};

te["vfile_new"] = { div:["g","va"], s:["ba mtn1",""], c:
[ 
	{ input:["g","voicefile_new-vfiles","file[]","","file"], ev:["","_file_upload"] }, 
	{ s:["c xx y07 gw cb",""] },
	{ ac:["d x y02","","_rm","x y n","&Cross;"] },
	{ p:["d x y02","nb"], s:["x y go cw","Uploading ..."] }, // todo: show progress
	{ div:["e"] },
]};

te["vfile_not_found"] = { s:["xx yy cr gp","Recording not found!"] };

te["vfile_vw_r"] = { div:["w35 gb","va"], c: /// playback widget
[
	{ div:["c"], uaudio:["%20","%0","%21"] },
	{ ac:["d x y","","_rm","x y h2","&Cross;"] },
	{ div:["e"] }
]};

te["audio_playback"] = { div:["w35 gb","va"], c: /// playback widget
[
	{ div:["c"], uaudio:["%20","%0","%21"] },
	{ ac:["d x y","","_rm","x y h2","&Cross;"] },
	{ div:["e"] }
]};

// --------------------------------

te["voicefile_del_"] = { div:["","va"], c:[ { arg:["o",null,"%0"] }, { arg:["o","source_id","0"] } ] };
te["voicefile_ed_"] = { div:["mb bb_w",""], c:
[
	{ p:["","play"] },
	{ div:["c bl bt bb gw"], ac:["ao x03 y02","vfile_vw_r-vfile_-va-play-@","_nd","x y",""], c:[ { img:["","","/voiceapps/images/play.png","14"] }, { arg:["id-0","",null] } ] },
	{ s:["c w30 x y bt bb br gw cd",null] },
	{ arg:["o",null,null] },
	{ ac:["d aa x",null,"_del","x y cb tc","&Cross;"] },
	{ ac:["d x t aa","","_mvup","h02 w02 awt",""] },
	{ ac:["d x t aa","","_mvdown","h02 w02 awb",""] },
	{ div:["e"], arg:["o","file_id",null] }
]};

te["moh_del"] = { voicefile_del_:["moh_id"] };
te["moh_ed"] = { div:["","va"], voicefile_ed_:["%7","%8","moh_id","%0", "moh_del","%7"] };
te["moh_new"] = { voicefile_ed_:["%0","%7","moh_id","", "moh_del","%0"] };

te["voicefile_del"] = { voicefile_del_:["voicefile_id"] };
te["voicefile_ed"] = { div:["","va"], voicefile_ed_:["%7","%8","voicefile_id","%0", "voicefile_del","%7"] };
te["voicefile_new"] = { voicefile_ed_:["%0","%7","voicefile_id","", "voicefile_del","%0"] };

te["voicefile_vw_r"] = { div:["w30 gws mb","va"], c:
[
	{ p:["","play"] },
	{ div:["c w03 bd "], ac:["ao","vfile_vw_r-vfile_-va-play-@","_nd","w03 x y",""], c:[ { img:["l02","","/voiceapps/images/play.png","16"] }, { arg:["id-0","","%7"]} ] },
	{ s:["c w05 xx y",":h:ms:15:"] },
	{ s:["d xx y","%8"] },
	{ div:["e"] }
]};


