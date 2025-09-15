
te["aiiv"] = { s:["c x","%0"] };

te["aiitag"] = { s:["c x bd cw gb mr mb","%0"] };

te["aiik"] = { s:["c x b","%0"] },

te["aii_usub"] = { usub:
[
"aii_transcript,aii_translation,aii_summarization,noop,aii_classification,aii_insights,aii_highlights",
"r_","%0",
"transcription,translation,summarization,ner,classification,insights,highlighting"
]};

te["aii"] = { c:
[
        { div:["cr"], c:[ { uo:["","noop","aiiv","aii","error"] }, { div:["e"]} ] },
	{ div:["cr"], c:[ { uo:["","noop","aiiv","aii","details","error_message"] }, { div:["e"]} ] },

	{ div:["cr"], c:[ { uo:["","noop","aiiv","aii","step"] }, { div:["e"]} ] },

	{ uo:["","noop","aii_usub","aii","step"] }
]};

te["aii_summary"] = { c:
[
	{ div:[""], c:[ { uo:["Case Summary","aiik","aiiv","aii","data","insights","case_summary"] }, { div:["e"]} ] },
]};

te["aii_highlights"] = { c:
[
	// annotated text
]};

te["aii_insights"] = { c:
[
	{ div:[""], c:[ { uo:["Case Summary","aiik","aiiv","aii","data","insights","case_summary"] }, { div:["e"]} ] },

	{ div:[""], c:[ { uo:["Persons","aiik","aiik","aiiv","aii","data","insights","named_entities","persons"] }, { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Organisations","aiik","aiiv","aii","data","insights","named_entities","organizations"] },  { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Locations","aiik","aiiv","aii","data","insights","named_entities","locations"] },  { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Dates","aiik","aiiv","aii","data","insights","named_entities","dates"] },  { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Contact Information","aiik","aiiv","aii","data","insights","named_entities","contact_information"] },  { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Category","aiik","aiitag","aii","data","insights","classification","category"] },  { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Interventions","aiik","aiiv","aii","data","insights","classification","interventions_needed"] },  { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Priority","aiik","aiiv","aii","data","insights","classification","priority_level"] },  { div:["e"]} ] },
	 
	{ div:[""], c:[ { uo:["Safety Immediate Actions","aiik","aiiv","aii","data","insights","case_management","safety_planning","immediate_actions"] },  { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Safety Long Term Measures","aiik","aiiv","aii","data","insights","case_management","safety_planning","long_term_measures"] }, { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Psychosocial Support Short Term Measures","aiik","aiiv","aii","data","insights","case_management","psychosocial_support","short_term"] }, { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Psychosocial Support Long Term Measures","aiik","aiiv","aii","data","insights","case_management","psychosocial_support","long_term"] }, { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Applicable Laws","aiik","aiiv","aii","data","insights","case_management","legal_protocols","applicable_laws"] }, { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Required Documents","aiik","aiiv","aii","data","insights","case_management","legal_protocols","required_documents"] }, { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Authorities To Contact","aiik","aiiv","aii","data","insights","case_management","legal_protocols","authorities_to_contact"] }, { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Immediate Medical Needs","aiik","aiiv","aii","data","insights","case_management","medical_protocols","immediate_needs"] }, { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Followup Medical Care","aiik","aiiv","aii","data","insights","case_management","medical_protocols","follow_up_care"] }, { div:["e"]} ] },
	
        { div:[""], c:[ { uo:["Red Flags","aiik","aiiv","aii","data","insights","risk_assessment","red_flags"] }, { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Potential Barriers","aiik","aiiv","aii","data","insights","risk_assessment","potential_barriers"] }, { div:["e"]} ] },
	{ div:[""], c:[ { uo:["Protective Factors","aiik","aiiv","aii","data","insights","risk_assessment","protective_factors"] }, { div:["e"]} ] },

        { div:[""], c:[ { uo:["Cultural Considerations","aiik","aiiv","aii","data","insights","cultural_considerations"] }, { div:["e"]} ] },
]};

te["aii_transcript"] = { div:[""], c:[ { uo:["transcript","aiik","aiiv","aii","data","transcript"] }, { div:["e"]} ] },

te["aii_translation"] = { div:[""], c:[ { uo:["translation","aiik","aiiv","aii","data","translated_transcript"] }, { div:["e"]} ] },

te["aii_summarization"] = {}

te["aii_classification"] = { c:
[
	{ div:[""], c:[ { uo:["persons","aiik","aiiv","aii","data","summary_entities","PERSON"] }, { div:["e"]} ] },
 	{ div:[""], c:[ { uo:["category","aiik","aiiv","aii","data","summary_classification","category"] }, { div:["e"]} ] },
 	{ div:[""], c:[ { uo:["confidence score","aiik","aiiv","aii","data","summary_classification","confidence"] }, { div:["e"]} ] },
]};

te["case_insights_txt"] = { s:["gy x y",null] }; // mime not application/json

te["case_insights"] = { umime:["case_insights_txt",":v:messages:src_msg", ":v:messages:src_mime", ":v:messages:src"] }

function uo (el, u, a, r, m)
{
	var o = ra[u[3]];
	for (var i=4; i<u.length; i++)
	{
		if (!o) return;
		if (!o[u[i]]) { console.error ("[uo] missing "+u[i]+" ("+i+")"); return; }
		o = o[u[i]];
	}
	if (Array.isArray(o))
	{
		if (o.length<1) return
		nd (el, te[u[1]], [], [u[0]], [0]);
		for (var i=0; i<o.length; i++)
		{
			// console.log (o[i]);
			nd (el, te[u[2]], [], [(""+o[i])], [0]);
		}
		return;
	}
	nd (el, te[u[1]], [], [u[0]], [0]);
	nd (el, te[u[2]], [], [(""+o)], [0]);
}

