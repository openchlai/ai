
te["case_attachment_del"] = { div:["l cr gp"], c:
[
	{ s:["c x y","Attachment Deleted"] },
	{ ac:["d ay ga","","_rm","x y h2","&Cross;"] },
	{ div:["e"] }
]};

te["case_attachment_"] = { div:["gbn mb"], c:
[
	{ div:[], c:
	[
		{ div:["d w03"], ac:["ao abs w03","case_attachment_del-attachments^del","_del","cb h2",""], c:
		[
			{ s:["x y h2 tc","&Cross;"] },
			{ div:[], c:[ { arg:["",".id","%0"] } ] }
		]},
		{ div:["e"] }
	]},
	{ div:["mr3","va"], ac:["ay","files","_file_download","x cb y02",""], c:
	[
		{ s:["c w28 x y",":v:attachments:file_name"] },
		{ s:["d w06 x y s tr",":v:attachments:file_size"] }, 
		{ div:["e"], c:[ { arg:["",".id",":v:attachments:file_id"] }, { arg:["","file","1"] } ] }
	]},
	{ div:[], arg:["o","attachment_id","%0"] }
]};

te["case_attachment"] = { div:["","va"], case_attachment_:[] };

te["case_attachment_upload"] = { div:["g","va"], c:
[
	{ div:["ba mb"], c:
	[ 
		{ input:["g","case_attachment_new-files","file[]","","file"], ev:["","_file_upload"] }, 
		{ s:["c xx y07 gw cb",""] },
		{ ac:["d x y02","","_rm","x y n","&Cross;"] },
		{ p:["d x y02","nb"], s:["x y go cw","Uploading ..."] }, // todo: show progress
		{ div:["e"] },
	]},
	{ div:["","case_attachment-attachments"], c:
	[
		{ p:["","o"], arg:["","case_id","%12"] }
	]}
]};

// ----------------------

te["case_attachment_vw_r"] = { div:["gws_ mb bd","va"], c:
[
	{ div:["","va"], ac:["ay","files","_file_download","x cb",""], c:
	[
		{ s:["c w28 x y",":v:attachments:file_name"] },
		{ s:["d w06 x y s tr",":v:attachments:file_size"] }, 
		{ div:["e"], c:[ { arg:["",".id",":v:attachments:file_id"] }, { arg:["","file","1"] } ] }
	]},
]};
