import json
import logging
import re
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def sanitize_json_response(response_text: str) -> str:
    """Extract and clean JSON from LLM response."""
    cleaned = re.sub(r'```json?\s*|\s*```', '', response_text, flags=re.DOTALL).strip()
    json_match = re.search(r'\{[^{}]*"case_summary"[^{}]*\}', cleaned, re.DOTALL)
    if json_match:
        return json_match.group(0)
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    return json_match.group(0) if json_match else cleaned

def call_ollama(model: str, prompt: str, endpoint: str = "http://localhost:11434/api/generate", timeout: int = 120) -> Optional[str]:
    """Call Ollama API with retries."""
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=2, status_forcelist=[502, 503, 504, 429])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    
    payload = {'model': model, 'prompt': prompt, 'stream': False}
    
    try:
        response = session.post(endpoint, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json().get('response', '').strip()
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return None

def generate_case_insights(transcript: str, classification_results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Input transcript + DistilBERT classification → Mistral → JSON insights
    Uses DistilBERT model's classification as the authoritative category source.

    Args:
        transcript: The call transcript text
        classification_results: DistilBERT model predictions with categories and confidence scores
    """

    # Format classification results for the prompt
    classification_section = ""

    # Set default values
    main_cat = "N/A"
    sub_cat = "N/A"
    intervention = "N/A"
    priority = "N/A"

    if classification_results:
        main_cat = classification_results.get('main_category', 'N/A')
        sub_cat = classification_results.get('sub_category', 'N/A')
        intervention = classification_results.get('intervention', 'N/A')
        priority = classification_results.get('priority', 'N/A')

        classification_section = f"""
=== PRE-CLASSIFIED CATEGORIES (MANDATORY - DO NOT CHANGE) ===

REQUIRED OUTPUT VALUES:
- primary_category: "{main_cat}"
- sub_category: "{sub_cat}"
- intervention: "{intervention}"
- priority: "{priority}"

Model Confidence: {classification_results.get('confidence', 0):.1%}

**CRITICAL**: Copy these exact values into your category_suggestions output. DO NOT create different categories.
=== END OF CLASSIFICATION ===
"""

    prompt = f"""
You are a Senior Child Protection Intake Specialist with 15+ years of experience in helpline crisis management and risk assessment. Your role is to:
- Analyze case narratives objectively
- Identify immediate safety concerns
- Assess risk levels based on established criteria
- Recommend appropriate interventions
- Extract key entities (names, locations, organizations, dates)
- Provide relevant tags for the case


=== CASE NARRATIVE ===
{transcript}

=== END OF NARRATIVE ===

{classification_section}




Evaluate the narrative and provide a comprehensive analysis in JSON format with these exact fields:

1. risk_level: One of "Critical", "High", "Medium", or "Low"
   - CRITICAL: Immediate danger to life or safety (active abuse, medical emergency, abandonment)
   - HIGH: Serious concern requiring urgent action within 24 hours (recent abuse, ongoing neglect, threats)
   - MEDIUM: Concern requiring follow-up within 72 hours (historical abuse, supervision concerns)
   - LOW: General concern for monitoring (parenting gaps, minor behavioral issues)

2. suggested_disposition: Specific recommended next action (e.g., "Immediate police referral", "Schedule home visit within 24h", "Provide information and referral")

3. rationale_summary: Brief explanation citing specific facts from the narrative (2-3 sentences)

4. confidence_score: Number between 0.0 and 1.0 based on information completeness and clarity

5. extracted_entities: Object with arrays for:
   - names: Array of person names mentioned
   - locations: Array of locations/addresses mentioned
   - organizations: Array of organizations/institutions mentioned
   - dates: Array of dates/timestamps mentioned

6. category_suggestions: Object with:
   - primary_category: MUST match the pre-classified Main Category exactly
   - sub_category: MUST match the pre-classified Sub-Category exactly
   - intervention: MUST match the pre-classified Intervention exactly
   - priority: MUST match the pre-classified Priority exactly
   - tags: Array of relevant tags/keywords based on the case narrative


CRITICAL CONSTRAINTS:
- MANDATORY: Use the exact pre-classified categories provided above. Do NOT generate your own categories.
- ONLY use facts explicitly stated in the narrative
- DO NOT infer, assume, or speculate beyond what is written
- If information is insufficient, state this in rationale and lower confidence score
- NEVER include personal opinions or judgments
- Adhere to mandatory reporting protocols
- Flag any ambiguous or contradictory information








**OUTPUT EXACTLY THIS JSON:**

{{
  "risk_level": "Critical|High|Medium|Low",
  "suggested_disposition": "Specific action",
  "rationale_summary": "2-3 sentences",
  "confidence_score": 0.85,
  "extracted_entities": {{
    "names": [],
    "locations": [],
    "organizations": [],
    "dates": []
  }},
  "category_suggestions": {{
    "primary_category": "{main_cat}",
    "sub_category": "{sub_cat}",
    "intervention": "{intervention}",
    "priority": "{priority}",
    "tags": ["relevant", "keywords"]
  }},
  "priority": "Critical|High|Medium|Low"
}}


OUTPUT REQUIREMENT:
Your response MUST be ONLY valid JSON. Do not include markdown code blocks, explanations, or any text outside the JSON object.
"""

    logger.info(" Calling Mistral...")
    response_text = call_ollama('mistral', prompt)
    
    if not response_text:
        return {"error": "Ollama unavailable"}
    
    # Parse
    try:
        insights = json.loads(response_text)
    except json.JSONDecodeError:
        sanitized = sanitize_json_response(response_text)
        insights = json.loads(sanitized)

    logger.info("Generated insights from Mistral with DistilBERT classification context")
    return insights

# TEST

if __name__ == "__main__":
    transcript = """Hello? Hello? Good evening? Good evening. You are speaking to Amido John from Sauti Child Helpline, how may I help you? I was asking. hhmm. Like this child help line inasaidia watoto aje? Thank you so much for the question, who am I speaking to? You are speaking to Evans Omondi from UNICEF. You are calling us from which county, Jacckline Nyaga? I'm in Narok. Which ward in Narok County? I don't know exactly but I'm in Narok. You don't know the ward or sub-county? Yeah. Okay, thank you so much for calling. Child Health Line deals with all child protection cases. Just in case there is a case of a minor who is being abused, you call the help line. Assistance is given based on the case that is reported. Okay. Because majorly we do referrals but mainly we offer psychosocial support to children who are actually survivors of abuse. Okay. Yes. So depending on your case, you are going to get the right referral and also a child is going to get a counselor to take them through psychosocial support. If they are around accessible areas where they can walk into the helpline one-on-one for counselling session, that is allowed. If it is just tele-counseling, that is also allowed and more preferred. Okay. What about if a child was gotten into drugs? Okay. So if there is a child who is gotten into drugs, again, I will go back to it depends on what the assistance, ama the need at hand. Okay. So if it is a child who is a drug addict and they want to be psychoeducated or psychotheraplized on drugs, that can happen because you have counselors who can do that. Also, if it is a parent who is reporting and they don't know what to do with their child who is a drug addict or who is into substance abuse, a counselor can also offer referrals depending on the case of the child and what the child has been doing to the extent of substance abuse. So when this is being done, is it done at a price? Child helpline offers psychosocial support or rather counseling for free. We don't charge our clients. Either in counseling or walk-in clients. Okay. Are you in Migori? No. Huh? No,  we are not in Migori. And that's why I was saying, tele-counseling can happen. It can be offered or a referral. Because we know there are level 4s and level 5s that offer counseling for free. So for example, if you are a child or there is a child or rather you are charged into substance abuse, we can refer them to level 4 or level 5. So you are going to work in a level 5 or level 4 and ask for counseling department or a youth friendly where this child is actually going to be given psychosocial support and be monitored. In a case where it has extended and they need rehabilitation, through the psychiatrist office or yes, through the psychiatrist office, they can be able to assist your child or the child actually. Do you think when someone is taken to rehabilitation, he can change his character? Yes. Provided, you see, behavior change only changes if the individual is willing to change. Because it's a lot of work and effort is needed. Okay. So if there is a change, there must be a need of change. Okay. From the individual. They are like, I admit I am a drug addict, I smoke bhang, or I take alcohol and I am dependent on it. However, I would want to actually leave it. And so finding you, where are you at? Location? We are currently in Nairobi. Uh huh. Yes. So when I want to bring my child, I have to come to Nairobi. Yes. And that's why we said, that's why I said, in a case where someone is not able to come as a walk-in client, they are going to be given tele-counseling. And in tele counseling, it's like the way we are talking one on one. So if it's a child who is calling, one on one with the child. Okay. But again, even in this tele-counseling, if it is a parent, we highly advise someone who is actually going to see the child physically, so that they can be able to see how is the child responding to whatever we are talking about. The assignment is, if the child do the assignment, can you physically see the assignments that this child has to go to the session. So we advise one on one counseling. That's why I am saying, if it's a child that you know, you can go to level four or level five. Okay. So, I want to, if this child is me right now speaking, and I'm a drug addict, I want to get out of it. That is the reason why. Okay. How old are you? I'm like 16 right now. Are you like 16 or you are 16? I'm 16. I'm 16 years. Okay. Yes. Where do you school? I'm learning at Nya Raj Secondary School. What? Nya Raj Secondary School. Can you just speak nicely in a way that you are audible and I can actually get the articulation of your words? Nya Raj Secondary. Nya Raj? Yes. Secondary. Is this like a boarding school? No, it's a day school. It's a day school. Yeah. Do your parents know that you are an addict of drugs? No, they don't know. Which drug are you taking? I want to quit both of them, alcohol and bhang. You take alcohol and your parents, they don't know? Like nafichanga white, umeshaskia that language that. Unafichanga white ukifanya nini? Unajua vile vitu zinafanyika. Like, the day has began then I spend at my friends. Sorry, ati unasema nini? Inahappeningi day, day saa zenye hawako. Ooh, unakunywanga day, day-time. Yeah. Mzazi wako anaitwa nani, wa kike ama wa kiume. Susan Kirigwa. Susan. So unakunywanga daily day time sa ile hawako na unakuywia kwao ama unakunywia kwa mabeshte? Kwa mabeshte tu, obvious. Unakuywia kwa mabeshte? Yeah. Okay. Are your recording things down or like uh... ama? yes, we take data mm-hmm that is mandatory but it's not data that will go anywhere that someone is actually going to know that Evans is a drug addict or anything or they actually called. okay. sawa sawa aa ee so ni alcohol umesema unakunywa na nini ingine? bangi pia na bhang. yeah. na i am sure kuna mali ilianzia. yeah. Ilianzia wapi? aah I can remember very well nilitumwa school fees mhm and then uh... i came back uh... and then uh... there was this friend of mine nikaenda kwake mm-hmm and then uh... he was my elder like alikuwa mkubwa mm-hmm so kukawa na avutatawa mi pia nika nika piga nilikuwa naitamani sana, unaona. Ulikuwa unatamani nini? nataka tuanze na story moja. ulizi kombine zote bangi na alcohol ama? hapana nilianzana na moja that was bhang. so bhang ndio ilikuwa ya kwanza. ilikuwa ya kwanza. na ni gani sahi you can't do without bangi. ni gani? bhang sana sana ndio uko addicted uko addict kwa bangi ata si pombe yeah uh... so uliwapata waki waki shikisha ukashikisha nao ee miki uh... sa hapo tukavuta tukavuta hadi nikaskia fiti hadi ni, ngoja. And then nikarudi tu kwa nyumba. yeah and then nikaficha white juu sikutaka my parents wajue. Ati? hukutaka wazae wajue. Yeah. Okay, so ukaficha white. Nikaficha white kama kawa. Ulitumia nini kuficha white? Like nilikuwa nimevaa specs. Ulikuwa umevaa specs? yeah and then i have my i had my perfume nilikuwa napiga. una do you wear glasses specs i want to is it like glasses ama ni hizi za jua gogos. vitu za jua tu hizi tu za jua. na hakuna mtu mwenye alikuuliza anything? hakuna mwenye aliniuliza. okay, yaa. sawa sawa so ee hivo ndio ulianza. so hao watu ni bado ni marafiki zako mpaka sahi. yaa they are my friends. they are your friends until now? Yes. Okay. So every other time you meet lazima mshikishe bangi. Lazima lazima. Haya. So, na unataka kuwacha, nini inafanya utake kuwacha? It's i don't feel like it's my life it's not my life. have you felt that you are going into a mess. you're saying this is not my life none mm-hmm yeah i have a mission i have somewhere to go. you know i need to go forward. Sahi umevuta bangi, sahizi tukiongea, sahi? yeah i'm really high i'm really high so how about we start by you calling and asking for help when you're not high. is that possible? okay. if possible will i get you? well any other counselor that you're going to be able to get for example will be will offer assistance because okay okay because"""
    insights = generate_case_insights(transcript)
    print(json.dumps(insights, indent=2, ensure_ascii=False))
