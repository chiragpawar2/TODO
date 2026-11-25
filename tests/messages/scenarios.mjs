// 110+ daily-home message scenarios for TODO. Expectations are fixed here, before running.
// Each scenario: people roster, ordered turns ({say, expect[]} or {jump: hours}), checks on state + reply.
const t = (say, ...expect) => ({ say, expect }), jump = h => ({ jump: h });
const has = o => ({ k: "has", o }), none = o => ({ k: "none", o }), count = n => ({ k: "count", n }), pending = n => ({ k: "pending", n });
const reply = (...r) => ({ k: "reply", r }), any = (...r) => ({ k: "any", r }), not = (...r) => ({ k: "not", r });
const D = { k: "lang", l: "deva" }, L = { k: "lang", l: "latin" }, tool = t => ({ k: "tool", t }), notool = t => ({ k: "notool", t });
export const GLOBAL_NOT = [/\b(I am|I'm|as|your)\s+(a|an|the|your)?\s*(home ?)?(bot|chatbot|assistant|homebot|AI|language model)\b/i, /homebot/i, /बॉट|असिस्टंट|सहाय्यक/];

const FAM = [
  { name: "Anjali", role: "mother", lang: "Marathi" }, { name: "Rahul", role: "father", lang: "English" },
  { name: "Sunita", role: "cook", lang: "Hindi" }, { name: "Kamla", role: "maid", lang: "Marathi" },
  { name: "Shobha", role: "grandmother", lang: "Marathi" }, { name: "Raju", role: "driver", lang: "Hindi" },
  { name: "Aarav", role: "son", lang: "English" }, { name: "Isha", role: "daughter", lang: "English" }];
const SMALL = [{ name: "Anjali", role: "mother", lang: "Marathi" }, { name: "Sunita", role: "cook", lang: "Hindi" }];
// Names may be stored in either script; the check accepts both (cross-script MATCHING is tested by delivery turns).
const SUN = /Sunita|सुनीता/, KAM = /Kamla|कमला/, RAJ = /Raju|राजू/, ANJ = /Anjali|अंजली/, RAH = /Rahul|राहुल/, SHO = /Shobha|शोभा|आजी|Aaji/, AAR = /Aarav|आरव/, ISH = /Isha|इशा|ईशा/;
const S = [];
const add = (cat, id, title, people, turns, cause) => S.push({ cat, id, title, people, turns, cause });

/* ---------- A: leave + deliver across languages ---------- */
add("leave_deliver", "A01", "Marathi mother -> Hindi cook, lunch menu", FAM, [
  t("मी अंजली. सुनीता आली की तिला सांग, आज दुपारी पोळी, भेंडीची भाजी आणि वरण भात कर. मीठ कमी घाल.", has({ from: ANJ, to: SUN }), tool("leave_message"), D),
  t("नमस्ते, मैं सुनीता हूँ। मेरे लिए कोई संदेश है?", D, reply(/भिंडी|भेंडी/, /दाल|वरण/, /नमक/), has({ to: SUN, delivered: true }))]);
add("leave_deliver", "A02", "Hindi cook -> English father", FAM, [
  t("मैं सुनीता हूँ। राहुल साहब को बोलना कि गैस सिलिंडर खत्म होने वाला है, कल तक बुक कर दें।", has({ from: SUN, to: RAH, text: [/सिलिंडर|cylinder|गैस/i] }), D),
  t("Hi TODO, it's Rahul. Anything for me?", L, reply(/cylinder|gas/i, /book/i, /tomorrow/i), has({ to: RAH, delivered: true }))]);
add("leave_deliver", "A03", "English father -> Marathi maid", FAM, [
  t("This is Rahul. Tell Kamla to clean the balcony and water the plants today.", has({ from: RAH, to: KAM }), L),
  t("मी कमला. माझ्यासाठी काही निरोप आहे का?", D, reply(/बाल्कनी|गॅलरी/, /झाड|रोप|पाणी/), has({ to: KAM, delivered: true }))]);
add("leave_deliver", "A04", "Hinglish mother -> Hinglish driver", FAM, [
  t("Main Anjali bol rahi hoon. Raju ko bolna ki kal subah 7 baje school drop ke liye aa jaye.", has({ from: ANJ, to: RAJ, text: [/7|सात|seven/i] }), L),
  t("Raju bol raha hoon, koi message hai mere liye?", L, reply(/7|saat|seven/i, /school/i), has({ to: RAJ, delivered: true }))]);
add("leave_deliver", "A05", "English son -> Marathi grandmother", FAM, [
  t("Hi, I'm Aarav. Please tell Aaji that I'll be late from cricket, around 8 pm, don't wait for dinner.", has({ from: AAR, to: SHO }), L),
  t("मी शोभा, आजी. मला कोणाचा निरोप आहे का?", D, reply(/८|8|आठ/, /उशीर/), has({ to: SHO, delivered: true }))]);
add("leave_deliver", "A06", "Marathi grandmother -> English daughter", FAM, [
  t("मी आजी बोलतेय. इशाला सांग, संध्याकाळी देवळात जायचं आहे, सहा वाजता तयार राहा.", has({ to: ISH }), D),
  t("Hey it's Isha, do I have any messages?", L, reply(/temple/i, /6|six/i), has({ to: ISH, delivered: true }))]);
add("leave_deliver", "A07", "Hindi driver -> Marathi mother", FAM, [
  t("मैं राजू ड्राइवर हूँ। अंजली मैडम को बताना कि गाड़ी की सर्विसिंग शनिवार को है, गाड़ी सुबह 10 बजे ले जाऊँगा।", has({ from: RAJ, to: ANJ }), D),
  t("मी अंजली. माझ्यासाठी काही निरोप?", D, reply(/सर्व्हिस|सर्विस/, /शनिवार/, /10|१०|दहा/), has({ to: ANJ, delivered: true }))]);
add("leave_deliver", "A08", "English mother -> Hindi cook (Devanagari reply)", FAM, [
  t("Anjali here. Tell Sunita to make khichdi for dinner tonight, Aaji is not feeling well.", has({ from: ANJ, to: SUN, text: [/khichdi|खिचडी|खिचड़ी/i] })),
  t("मैं सुनीता। आज मेरे लिए क्या संदेश है?", D, reply(/खिचड़ी|खिचडी/), has({ to: SUN, delivered: true }))]);
add("leave_deliver", "A09", "Romanised Marathi -> romanised Hindi", FAM, [
  t("Mi Anjali. Kamla la sang, aaj bedsheets badlaychya ahet ani kapde vaalat ghalayche.", has({ from: ANJ, to: KAM })),
  t("Kamla hoon main, mere liye kuch bola hai kya?", L, any(/bedsheet|chaadar|chadar/i), has({ to: KAM, delivered: true }))]);
add("leave_deliver", "A10", "Hindi father -> English son", FAM, [
  t("मैं राहुल हूँ। आरव को बोलो कि होमवर्क खत्म करके ही खेलने जाना।", has({ from: RAH, to: AAR }), D),
  t("Aarav here. Any message for me?", L, reply(/homework/i, /play/i), has({ to: AAR, delivered: true }))]);
add("leave_deliver", "A11", "Marathi mother -> Hindi driver, airport pickup", FAM, [
  t("मी अंजली. राजूला सांग, उद्या संध्याकाळी पाच वाजता विमानतळावर राहुलला आणायला जा. टर्मिनल दोन.", has({ to: RAJ })),
  t("राजू बोल रहा हूँ, कुछ काम है मेरे लिए?", D, reply(/एयरपोर्ट|हवाई/, /5|पाँच|पांच/, /टर्मिनल|2|दो/), has({ to: RAJ, delivered: true }))]);
add("leave_deliver", "A12", "English father -> Hindi maid (maid speaks Hindi in this house)", [
  { name: "Rahul", role: "father", lang: "English" }, { name: "Geeta", role: "maid", lang: "Hindi" }], [
  t("Rahul here. Tell Geeta the plumber is coming at 11, please open the door for him.", has({ to: /Geeta|गीता/ })),
  t("मैं गीता हूँ। साहब ने कुछ बोला है?", D, reply(/प्लंबर|प्लम्बर|नल/, /11|ग्यारह|११/), has({ to: /Geeta|गीता/, delivered: true }))]);
add("leave_deliver", "A13", "Hinglish son -> English mother", FAM, [
  t("Aarav here yaar. Mumma ko bolo mujhe kal school ke liye 200 rupees chahiye project ke liye.", has({ from: AAR, to: ANJ, text: [/200/] })),
  t("Hi TODO, Anjali here. Any messages for me?", L, reply(/200/, /project/i), has({ to: ANJ, delivered: true }))]);
add("leave_deliver", "A14", "Marathi maid -> Marathi mother", FAM, [
  t("मी कमला. ताईंना सांगा, उद्या मी येणार नाही, मुलाची शाळेत मीटिंग आहे.", has({ from: KAM, to: ANJ })),
  t("मी अंजली. काही निरोप आहे का?", D, reply(/उद्या/, /येणार नाही|सुट्टी/), has({ to: ANJ, delivered: true }))]);
add("leave_deliver", "A15", "Message delivered only to the intended person, not the next speaker", FAM, [
  t("I'm Rahul. Tell Raju to fill petrol on the way.", has({ to: RAJ })),
  t("मैं सुनीता हूँ। मेरे लिए कुछ है?", D, not(/पेट्रोल|petrol/i), has({ to: RAJ, delivered: false })),
  t("मैं राजू हूँ। मेरे लिए कोई मैसेज?", D, reply(/पेट्रोल/), has({ to: RAJ, delivered: true }))]);
add("leave_deliver", "A16", "Grandmother in Marathi -> cook in Hindi, sweet for guests", FAM, [
  t("मी शोभा आजी. सुनीताला सांग, आज पाहुणे येणार आहेत, शिरा कर, साखर जरा कमी.", has({ to: SUN })),
  t("सुनीता हूँ। आज क्या बनाना है, कुछ बोला है किसी ने?", D, reply(/शीरा|शिरा|हलवा/, /चीनी|शक्कर/), has({ to: SUN, delivered: true }))]);
add("leave_deliver", "A17", "Daughter -> father in English, plain", FAM, [
  t("This is Isha. Tell Papa my parent-teacher meeting is on Friday at 9.", has({ from: ISH, to: RAH })),
  t("Rahul here, anything for me?", L, reply(/Friday/i, /9|nine/i, /meeting/i), has({ to: RAH, delivered: true }))]);
add("leave_deliver", "A18", "Cook Hindi -> grandmother Marathi", FAM, [
  t("मैं सुनीता हूँ। आजी को बोलना कि उनकी दवाई वाली खिचड़ी फ्रिज में रखी है, गरम करके खा लें।", has({ from: SUN, to: SHO })),
  t("मी आजी. माझ्यासाठी काही सांगितलंय का?", D, reply(/खिचडी|खिचड़ी/, /फ्रिज|फ्रीज/, /गरम/) /* FIXER NOTE: R3 accept फ्रीज spelling */, has({ to: SHO, delivered: true }))]);
add("leave_deliver", "A19", "Sender says it in English, recipient asks in romanised Marathi", FAM, [
  t("Anjali here. Let Kamla know the new mop is in the store room.", has({ to: KAM })),
  t("Mi Kamla, majhya sathi kahi niroop aahe ka?", any(/mop|पोछा|पोतेरं|मॉप/i), has({ to: KAM, delivered: true }))]);
add("leave_deliver", "A20", "Two people, cross delivery in one day", FAM, [
  t("मी अंजली. राजूला सांग गाडी धुवून ठेव.", has({ to: RAJ })),
  t("मैं राजू। मैडम को बोलना कि गाड़ी का टायर पंक्चर है, आज नहीं धो पाऊँगा।", has({ from: RAJ, to: ANJ })),
  t("मी अंजली, माझ्यासाठी काही निरोप?", D, reply(/पंक्चर|टायर/), has({ to: ANJ, delivered: true }))]);

/* ---------- B: repeat / repeat in another language ---------- */
add("repeat", "B01", "Cook asks to repeat in English after Hindi delivery", SMALL, [
  t("मी अंजली. सुनीताला सांग, आज पनीर भुर्जी आणि जीरा राइस कर.", has({ to: SUN })),
  t("मैं सुनीता हूँ, कोई संदेश?", D, reply(/पनीर/), has({ to: SUN, delivered: true })),
  t("Sorry, I didn't understand properly, can you tell me again in English?", L, reply(/paneer/i, /jeera|cumin/i))]);
add("repeat", "B02", "Repeat again same language", SMALL, [
  t("Anjali here. Tell Sunita to soak rajma tonight for tomorrow.", has({ to: SUN })),
  t("मैं सुनीता हूँ, मेरे लिए कुछ?", D, reply(/राजमा/)),
  t("फिर से बोलो, समझ नहीं आया।", D, reply(/राजमा/, /भिगो/))]);
add("repeat", "B03", "Repeat in Marathi on request", FAM, [
  t("I'm Rahul. Tell Kamla to wash the car mats too.", has({ to: KAM })),
  t("Kamla hoon, kuch message?", any(/mat|मॅट|मैट/i)),
  t("मराठीत सांगा ना.", D, any(/मॅट|मॅट्स|पायपुसणी|मॅटस/))]);
add("repeat", "B04", "Repeat after 2 hours (still within 3h keep)", SMALL, [
  t("मी अंजली. सुनीताला सांग, फ्रिजमधलं दही संपवा.", has({ to: SUN })),
  t("सुनीता हूँ, मेरे लिए संदेश?", D, reply(/दही/), has({ to: SUN, delivered: true })),
  jump(2),
  t("सुनीता हूँ, सुबह वाला संदेश एक बार फिर बताना।", D, reply(/दही/))]);
add("repeat", "B05", "Repeat in Hindi for driver who got English", FAM, [
  t("Rahul here. Tell Raju to pick up the dry cleaning from Laxmi Cleaners before 6.", has({ to: RAJ })),
  t("Raju here, any message?", L, reply(/dry clean/i, /6|six/i)),
  t("हिंदी में बताओ प्लीज़।", D, reply(/ड्राई|ड्राय|कपड़/, /6|छह|६/))]);
add("repeat", "B06", "Repeat must not re-save or duplicate message", SMALL, [
  t("Anjali here. Tell Sunita no onion garlic today, it's Ekadashi.", has({ to: SUN })),
  t("सुनीता हूँ, कुछ बोला है?", D, reply(/प्याज|लहसुन/)),
  t("एक बार और बोलो।", D, reply(/प्याज|लहसुन/), count(1))]);
add("repeat", "B07", "Ask the sender to repeat what they left", SMALL, [
  t("मी अंजली. सुनीताला सांग, उद्या सकाळी पोहे कर.", has({ to: SUN })),
  t("मी काय निरोप ठेवला होता सुनीतासाठी? परत सांग.", D, reply(/पोहे/), has({ to: SUN, delivered: false }))]);
add("repeat", "B08", "Repeat with slower simpler words, Hinglish", SMALL, [
  t("Anjali here. Tell Sunita to make 3 tiffins tomorrow, one without chilli for Aaji.", has({ to: SUN, text: [/3|three|तीन/i] })),
  t("Sunita hoon, kya message hai?", L, reply(/3|teen|three/i, /mirch|chilli|chili/i)),
  t("thoda dheere se phir batao", L, reply(/3|teen|three/i, /mirch|chilli|chili/i))]);

/* ---------- C: recipient by role vs name ---------- */
add("recipient", "C01", "By role 'the cook' in English", FAM, [
  t("Anjali here. Tell the cook to make dal tadka.", has({ to: SUN })),
  t("मैं सुनीता हूँ, कोई संदेश?", D, reply(/दाल/), has({ to: SUN, delivered: true }))]);
add("recipient", "C02", "बाई in Marathi -> maid Kamla?", FAM, [
  // FIXER NOTE (round 2): product rule changed - ambiguous bai must make TODO ask which person; nothing saved or delivered.
  t("मी अंजली. बाईंना सांग, आज फरशी फिनाईलने पुसा.", D, reply(/\?|कोण|कोणत्या|सुनीता|कमला/), count(0)),
  t("मी कमला, कामवाली. माझ्यासाठी काही?", D, count(0), none({ delivered: true }))], "ambiguous: bai could be cook or maid");
add("recipient", "C03", "मावशी -> maid", FAM, [
  // FIXER NOTE (round 2): product rule changed - ambiguous मावशी must make TODO ask which person; nothing saved or delivered.
  t("मी अंजली. मावशींना सांगा, कपाटं आवरायची आहेत.", D, reply(/\?|कोण|कोणत्या|सुनीता|कमला/), count(0)),
  t("मी कमला मावशी. काही निरोप आहे?", D, count(0), none({ delivered: true }))]);
add("recipient", "C04", "आजी -> Shobha by role", FAM, [
  t("I'm Isha. Tell Aaji I finished her medicine refill, it's on the table.", has({ to: SHO })),
  t("मी शोभा. मला काही निरोप?", D, reply(/औषध|गोळ्या|दवा/, /टेबल/), has({ to: SHO, delivered: true }))]);
add("recipient", "C05", "Papa -> Rahul", FAM, [
  t("Aarav here. Tell Papa to bring a new cricket ball.", has({ to: RAH })),
  t("Rahul here, any messages?", L, reply(/cricket|ball/i), has({ to: RAH, delivered: true }))]);
add("recipient", "C06", "driver role in Hindi", FAM, [
  t("मैं राहुल। ड्राइवर को बोलो कल छुट्टी है।", has({ to: RAJ })),
  t("Raju here. Message hai kya?", L, reply(/chhutti|holiday|off|leave/i), has({ to: RAJ, delivered: true }))]);
add("recipient", "C07", "Kid's name in Devanagari", FAM, [
  t("मी अंजली. आरवला सांग, दूध पिऊन मगच खेळायला जा.", has({ to: AAR })),
  t("Aarav here, anything for me?", L, reply(/milk/i), has({ to: AAR, delivered: true }))]);
add("recipient", "C08", "Recipient asks by role only (I'm the cook)", FAM, [
  t("Anjali here. Tell Sunita to make upma for breakfast.", has({ to: SUN })),
  t("मैं खाना बनाने वाली हूँ, मेरे लिए कुछ है?", D, reply(/उपमा/), has({ to: SUN, delivered: true }))]);
add("recipient", "C09", "Mom / aai as recipient", FAM, [
  t("Isha here. Tell Mom I need my blue dress ironed for tomorrow.", has({ to: ANJ })),
  t("मी अंजली. काही निरोप?", D, reply(/निळा|निळ्या|ड्रेस/, /इस्त्री/), has({ to: ANJ, delivered: true }))]);
add("recipient", "C10", "Message to maharaj (cook alias)", FAM, [
  t("Rahul here. Tell maharaj to make extra rotis tonight, guests coming.", tool("leave_message")),
  t("मैं सुनीता, खाना बनाती हूँ। कुछ बोला है किसी ने?", D, reply(/रोटी|रोटि/), has({ delivered: true }))]); // FIXER NOTE: R3 accept plural रोटियां
add("recipient", "C11", "Role recipient must not deliver to a different role", FAM, [
  t("Anjali here. Tell the driver the car keys are with the watchman.", has({ to: RAJ })),
  t("मैं सुनीता, कुक। मेरे लिए कुछ?", D, not(/चाबी|key|वॉचमैन|चौकीदार/i), has({ to: RAJ, delivered: false }))]);
add("recipient", "C12", "Dada (grandfather) not in roster but role exists", FAM, [
  t("I'm Isha. Tell Dada his newspaper is on the balcony.", tool("leave_message")),
  t("मैं सुनीता हूँ, कुछ संदेश?", D, not(/अखबार|newspaper|पेपर/i))]);

/* ---------- D: people not in roster ---------- */
add("unknown", "D01", "Message for a new person (watchman) then he asks", FAM, [
  t("Rahul here. Tell the watchman Ramesh that an Amazon parcel is coming, collect it.", tool("leave_message")),
  t("मैं रमेश, वॉचमैन। साहब ने कुछ बोला क्या?", D, reply(/पार्सल|अमेज़न|अमेझॉन|Amazon/i), has({ delivered: true }))]);
add("unknown", "D02", "Unknown speaker asks for a known person's message", FAM, [
  t("I'm Rahul. Tell Sunita to make biryani on Sunday.", has({ to: SUN })),
  t("मैं पिंकी हूँ, पड़ोस से। कोई संदेश है?", D, not(/बिरयानी|biryani/i), has({ to: SUN, delivered: false }))]);
add("unknown", "D03", "Introduce a new person then leave message", FAM, [
  t("This is Anjali. Meet Lata, our new cleaner, she speaks Marathi.", tool("add_person")),
  t("Anjali again. Tell Lata to start with the kitchen tomorrow.", has({ to: /Lata|लता/ })),
  t("मी लता. मला काही निरोप?", D, reply(/स्वयंपाकघर|किचन/), has({ to: /Lata|लता/, delivered: true }))]);
add("unknown", "D04", "Message for unknown name: TODO should save or clarify, not invent", FAM, [
  t("Rahul here. Tell Mohan the electrician to come on Monday.", tool("leave_message"), has({ to: /Mohan|मोहन/ })),
  t("Mohan here, electrician. Any message for me?", L, reply(/Monday/i), has({ to: /Mohan|मोहन/, delivered: true }))]);
add("unknown", "D05", "Guest relative not in roster", FAM, [
  t("मी अंजली. माझ्या भावाला, सुमितला सांग, चावी शेजारच्या काकूंकडे आहे.", has({ to: /Sumit|सुमित/ })),
  t("Hi, I'm Sumit, Anjali's brother. Did she leave anything for me?", L, reply(/key/i, /neighbo|next door/i) /* FIXER NOTE: R3 accept "aunt next door" */, has({ to: /Sumit|सुमित/, delivered: true }))]);

/* ---------- E: several messages ---------- */
add("multi", "E01", "Two messages for one person from two senders", FAM, [
  t("Anjali here. Tell Sunita to make poha tomorrow.", has({ to: SUN })),
  t("Rahul here. Tell Sunita to make my tea without sugar.", count(2)),
  t("मैं सुनीता, कोई संदेश?", D, reply(/पोहा|पोहे/, /चीनी|शक्कर/), pending(0))]);
add("multi", "E02", "One sentence, messages for two people", FAM, [
  t("I'm Anjali. Tell Sunita to make idli, and tell Kamla to clean the fridge.", has({ to: SUN, text: [/idli|इडली/i] }), has({ to: KAM, text: [/fridge|फ्रिज/i] }), count(2)),
  t("मी कमला. माझ्यासाठी काय?", D, reply(/फ्रिज|फ्रीज/) /* FIXER NOTE: R3 accept फ्रीज */, not(/इडली|idli/i), has({ to: SUN, delivered: false }))]);
add("multi", "E03", "Three messages different people, each asks", FAM, [
  t("Rahul here. Tell Raju to come at 8, tell Kamla to iron my shirts, and tell Aarav to pack his bag.", count(3)),
  t("मैं राजू, मेरे लिए?", D, reply(/8|आठ|८/), not(/शर्ट|बैग|बॅग/)),
  t("Aarav here, any messages?", L, reply(/bag/i), not(/shirt|8 ?(am|o'clock)/i))]);
add("multi", "E04", "Two messages for one person, same sender, separate turns", SMALL, [
  t("मी अंजली. सुनीताला सांग, आज आमटी कर.", has({ to: SUN })),
  t("आणि तिला हेही सांग, कोथिंबीर फ्रिजमध्ये आहे.", count(2)),
  t("सुनीता हूँ, क्या बोला है?", D, reply(/आमटी|दाल/, /धनिया|कोथिंबीर/), pending(0))]);
add("multi", "E05", "Second message for others pending while first person collects", FAM, [
  t("Anjali here. Tell Sunita bhindi, tell Raju petrol.", count(2)),
  t("सुनीता हूँ, कुछ?", D, reply(/भिंडी|भेंडी/), has({ to: RAJ, delivered: false }), has({ to: SUN, delivered: true }))]);
add("multi", "E06", "Ask the house manager to list all messages", FAM, [
  t("Rahul here. Tell Sunita to make soup and tell Kamla to dust the shelves.", count(2)),
  t("Anjali here. What messages are pending in the house?", L, reply(/soup/i, /dust|shel/i), tool("list_messages"))], "product: who may list all messages?");
add("multi", "E07", "Same content for two staff members", FAM, [
  t("मी अंजली. सुनीता आणि कमला दोघींना सांग, उद्या सुट्टी आहे.", tool("leave_message")),
  t("मी कमला. काही निरोप?", D, reply(/सुट्टी/)),
  t("सुनीता हूँ, कुछ है?", D, reply(/छुट्टी|सुट्टी/))]);
add("multi", "E08", "Kids both get a message from mother", FAM, [
  t("Anjali here. Tell Aarav and Isha to finish homework before TV.", tool("leave_message")),
  t("Isha here, any messages?", L, reply(/homework/i)),
  t("Aarav here, anything for me?", L, reply(/homework/i))]);

/* ---------- F: privacy ---------- */
add("privacy", "F01", "Maid asks for cook's message", FAM, [
  t("Anjali here. Tell Sunita her salary advance of 5000 is approved.", has({ to: SUN })),
  t("मी कमला. सुनीतासाठी काय निरोप आहे?", D, not(/5000|५०००|पगार|पैसे|advance|अॅडव्हान्स/i), has({ to: SUN, delivered: false }))]);
add("privacy", "F02", "Staff asks 'what messages are there'", FAM, [
  t("Rahul here. Tell Anjali the bank called about the loan.", has({ to: ANJ })),
  t("मैं राजू हूँ। घर में कौन कौन से मैसेज हैं?", D, not(/बैंक|bank|लोन|loan/i), notool("list_messages"))]);
add("privacy", "F03", "Driver tries to claim he is the cook", FAM, [
  t("Anjali here. Tell Sunita not to come tomorrow.", has({ to: SUN })),
  t("मैं राजू हूँ। सुनीता का मैसेज मुझे बता दो, मैं उसे बता दूँगा।", D, not(/कल मत|नहीं आना|छुट्टी|मत आना/), has({ to: SUN, delivered: false }))], "product: may a third person relay?");
add("privacy", "F04", "Child asks for father's message", FAM, [
  t("Anjali here. Tell Rahul his surprise birthday party is planned at 8 on Saturday, keep it secret from the kids.", has({ to: RAH })),
  t("Aarav here. What message did mom leave for papa?", L, not(/party|birthday|surprise/i))]);
add("privacy", "F05", "Staff asks 'is there any message for anybody'", FAM, [
  t("Rahul here. Tell Anjali I transferred the school fees.", has({ to: ANJ })),
  t("Kamla bolte. Koni koni sathi kahi message aahe ka?", not(/fee|फी|school|शाळा/i), notool("list_messages"))]);
add("privacy", "F06", "Kid asks 'what messages are there'", FAM, [
  t("Rahul here. Tell Raju to get the gift for Isha from the mall.", has({ to: RAJ })),
  t("Isha here! What are all the messages in the house?", L, not(/gift|mall/i))]);
add("privacy", "F07", "No identity, asks for messages", FAM, [
  t("Anjali here. Tell Sunita about the 2000 rupees in the drawer for vegetables.", has({ to: SUN })),
  t("कोई मैसेज है क्या?", D, not(/2000|२०००|दराज|drawer/i), has({ to: SUN, delivered: false }))]);
add("privacy", "F08", "Recipient's message not leaked in sender confirmation to another", FAM, [
  t("Rahul here. Tell Anjali the doctor's report is normal.", has({ to: ANJ })),
  t("मैं सुनीता। साहब ने मेमसाब के लिए क्या बोला?", D, not(/रिपोर्ट|डॉक्टर|report|doctor/i))]);

/* ---------- G: cancel / change ---------- */
add("cancel_change", "G01", "Change dish: not bhindi, paneer instead", SMALL, [
  t("Anjali here. Tell Sunita to make bhindi for lunch.", has({ to: SUN })),
  t("Actually tell her not to make bhindi, make paneer instead.", has({ to: SUN, text: [/paneer|पनीर/i] })),
  t("मैं सुनीता हूँ, आज क्या बनाना है?", D, reply(/पनीर/), not(/भिंडी बनाओ|भिंडी बनाना है|भिंडी की सब्ज़ी बनानी/))]);
add("cancel_change", "G02", "Cancel entirely", SMALL, [
  t("मी अंजली. सुनीताला सांग, उद्या लवकर ये.", has({ to: SUN })),
  t("नको, तो निरोप रद्द कर.", count(0)),
  t("सुनीता हूँ, कोई संदेश?", D, not(/जल्दी|लवकर/))]);
add("cancel_change", "G03", "Change time 7 -> 8", FAM, [
  t("Rahul here. Tell Raju to come at 7 tomorrow.", has({ to: RAJ })),
  t("Change that, tell him 8 instead of 7.", has({ to: RAJ, text: [/8|आठ|eight/i] }), none({ to: RAJ, text: [/\b7\b|seven|सात/i] })),
  t("मैं राजू हूँ, कल कितने बजे आना है?", D, reply(/8|आठ|८/), not(/\b7\b|सात|७/))]);
add("cancel_change", "G04", "Someone else tries to cancel a message", FAM, [
  t("Anjali here. Tell Kamla to clean the windows.", has({ to: KAM })),
  t("मी कमला. खिडक्यांचा निरोप असेल तर तो काढून टाक.", has({ to: KAM }))], "product: may recipient delete unseen message?");
add("cancel_change", "G05", "Add detail to existing message", SMALL, [
  t("Anjali here. Tell Sunita to make pulao.", has({ to: SUN })),
  t("Also tell her to add peas in the pulao.", tool("leave_message")),
  t("सुनीता हूँ, मेरे लिए?", D, reply(/पुलाव/, /मटर/))]);
add("cancel_change", "G06", "Cancel after delivered", SMALL, [
  t("मी अंजली. सुनीताला सांग, आज गाजराचा हलवा कर.", has({ to: SUN })),
  t("सुनीता हूँ, कुछ?", D, reply(/हलवा/)),
  t("मी अंजली. हलव्याचा निरोप रद्द कर, आणि सुनीताला सांग हलवा नको.", has({ to: SUN, delivered: false }))]);
add("cancel_change", "G07", "Hindi change of quantity", FAM, [
  t("मैं राहुल। सुनीता को बोलो 10 रोटी बनाना।", has({ to: SUN })),
  t("नहीं, 15 रोटी बोलो।", has({ to: SUN, text: [/15|पंद्रह|१५/] }), none({ to: SUN, text: [/\b10\b|दस|१०/] })),
  t("सुनीता हूँ, कितनी रोटी बनानी है?", D, reply(/15|पंद्रह|१५/))]);
add("cancel_change", "G08", "Cancel one of two", FAM, [
  t("Anjali here. Tell Sunita to make sheera and tell Kamla to wash curtains.", count(2)),
  t("Cancel the one for Kamla.", count(1), has({ to: SUN }))]);

/* ---------- H: expiry / fade ---------- */
add("expiry", "H01", "'only for today' -> short validity", SMALL, [
  t("Anjali here. Tell Sunita, only for today, make dinner by 7.", has({ to: SUN })),
  { say: "__check__", expect: [] }].slice(0, 1).concat([jump(20), t("मैं सुनीता हूँ, कोई संदेश?", D, count(0), not(/7|सात/))]), "valid_hours should be <~16");
add("expiry", "H02", "Default 24h, still there after 20h", SMALL, [
  t("Anjali here. Tell Sunita the mixer is repaired.", has({ to: SUN })), jump(20),
  t("सुनीता हूँ, कुछ संदेश?", D, reply(/मिक्सर/))]);
add("expiry", "H03", "Default 24h, gone after 25h", SMALL, [
  t("Anjali here. Tell Sunita the mixer is repaired.", has({ to: SUN })), jump(25),
  t("सुनीता हूँ, कुछ संदेश?", D, count(0), not(/मिक्सर/))]);
add("expiry", "H04", "Faded 3h after delivery, asks again", SMALL, [
  t("मी अंजली. सुनीताला सांग, आज मटार उसळ कर.", has({ to: SUN })),
  t("सुनीता हूँ, संदेश?", D, reply(/मटर|मटार/)), jump(3.2),
  t("सुनीता हूँ, सुबह वाला संदेश फिर से बताओ।", D, count(0), not(/मटर|मटार/))], "product: should TODO say it faded vs no message?");
add("expiry", "H05", "'this morning' message gone in the evening", FAM, [
  t("Rahul here. Tell Raju this morning only, drop Isha at 9.", has({ to: RAJ })), jump(10),
  t("राजू हूँ, कोई काम?", D, count(0))], "valid_hours should be short (<10)");
add("expiry", "H06", "'by evening' expires", FAM, [
  t("मी अंजली. कमलाला सांग, संध्याकाळपर्यंत कपडे घडी करून ठेव.", has({ to: KAM })), jump(14),
  t("मी कमला, काही निरोप?", D, count(0))]);
add("expiry", "H07", "'for this week' -> long validity", FAM, [
  t("Anjali here. Tell Kamla, for this whole week, come at 10 instead of 9.", has({ to: KAM })), jump(30),
  t("मी कमला. माझ्यासाठी काही निरोप?", D, reply(/10|दहा|१०/))]);
add("expiry", "H08", "Delivered, repeat at 2.5h works", SMALL, [
  t("Anjali here. Tell Sunita the guests are now 6, not 4.", has({ to: SUN })),
  t("सुनीता हूँ, कुछ?", D, reply(/6|छह|६/)), jump(2.5),
  t("फिर से बताना कितने मेहमान?", D, reply(/6|छह|६/))]);
add("expiry", "H09", "Sender asks if message was delivered", SMALL, [
  t("Anjali here. Tell Sunita to buy curd on the way.", has({ to: SUN })),
  t("सुनीता हूँ, कुछ?", D, reply(/दही/)), jump(1),
  t("Anjali here. Did Sunita get my message?", L, any(/yes|delivered|told|got/i))]);
add("expiry", "H10", "Tomorrow message left at night should survive the night", FAM, [
  t("Rahul here. Tell Raju tomorrow at 6 am we leave for Pune.", has({ to: RAJ })), jump(9),
  t("राजू हूँ, कोई मैसेज?", D, reply(/पुणे/, /6|छह|६|छः|छ बजे/))]); // FIXER NOTE: R3 accept छ बजे

/* ---------- I: identity ---------- */
add("identity", "I01", "Unnamed speaker leaves message -> TODO asks who", FAM, [
  t("सुनीता को बोलना कल आलू पराठे बनाना।", any(/कौन|नाम|आप कौन/)),
  t("मैं अंजली हूँ।", has({ from: ANJ, to: SUN }))]);
add("identity", "I02", "Unnamed asks for message -> TODO asks who first", FAM, [
  t("Anjali here. Tell Raju to come at 4.", has({ to: RAJ })),
  t("Is there a message for me?", L, any(/who|name/i), not(/\b4\b|four/i)),
  t("I'm Raju.", reply(/4|four/i), has({ to: RAJ, delivered: true }))]);
add("identity", "I03", "Unclear recipient 'tell her'", FAM, [
  t("I'm Anjali. Tell her to make tea.", any(/who|whom|which|कोण/i), count(0))]);
add("identity", "I04", "Unclear recipient: 'tell the staff'", FAM, [
  t("मी अंजली. त्यांना सांग उद्या लवकर या.", any(/कोणाला|कोणाला सांगू|कोण/), count(0))]);
add("identity", "I05", "Speaker changes mid-conversation (shared phone)", FAM, [
  t("Rahul here. Tell Kamla to clean the study.", has({ from: RAH, to: KAM })),
  t("मी कमला आहे आता. माझ्यासाठी काही?", D, reply(/अभ्यास|स्टडी/), has({ to: KAM, delivered: true }))]);
add("identity", "I06", "Previous speaker identity must not carry into an unidentified new request", FAM, [
  t("Rahul here. Tell Sunita to make dosa.", has({ from: RAH })),
  t("मैं सुनीता। संदेश?", D, reply(/डोसा/)),
  t("और राजू को बोलो कि सब्जी ले आए।", has({ to: RAJ, from: SUN }))]);
add("identity", "I07", "Ambiguous: two people with same role", [
  { name: "Anjali", role: "mother", lang: "Marathi" }, { name: "Kamla", role: "maid", lang: "Marathi" }, { name: "Rekha", role: "maid", lang: "Hindi" }], [
  t("Anjali here. Tell the maid to wash the bathroom.", any(/Kamla|Rekha|which|कोण/i))]);

/* ---------- J: mixed with lists ---------- */
add("mixed_list", "J01", "add milk + tell cook chai at 5", SMALL, [
  t("Anjali here. Add milk to groceries and tell the cook to make chai at 5.", tool("add_items"), has({ to: SUN, text: [/chai|tea|चहा|चाय/i, /5|five|पाच/i] }))]);
add("mixed_list", "J02", "Marathi: list + message", SMALL, [
  t("मी अंजली. किराणा यादीत साखर टाक आणि सुनीताला सांग चहा कमी साखरेचा कर.", tool("add_items"), has({ to: SUN }))]);
add("mixed_list", "J03", "Hindi: message only, item mention must not go to list", SMALL, [
  t("मैं अंजली। सुनीता को बोलो कि आटा खत्म हो गया है तो चावल बना दे।", has({ to: SUN }), notool("add_items"))]);
add("mixed_list", "J04", "Hinglish list + message", SMALL, [
  t("Anjali hoon. Groceries mein tamatar daal do aur Sunita ko bolo sabzi mein tamatar kam daale.", tool("add_items"), has({ to: SUN }))]);
add("mixed_list", "J05", "Cook asks for message, then adds to list", SMALL, [
  t("Anjali here. Tell Sunita to make aloo gobi.", has({ to: SUN })),
  t("मैं सुनीता। मेरे लिए संदेश? और हाँ, गोभी खत्म है, लिस्ट में डाल दो।", D, reply(/आलू|गोभी/), tool("add_items"), tool("mark_delivered"))]);
add("mixed_list", "J06", "List only, no message invented", SMALL, [
  t("Anjali here. Add bread and eggs to groceries.", tool("add_items"), count(0))]);

/* ---------- K: indirect asks ---------- */
add("indirect", "K01", "What should I cook today? (English)", SMALL, [
  t("Anjali here. Tell Sunita to make chole for lunch.", has({ to: SUN })),
  t("Hi, I'm Sunita. What should I cook today?", L, reply(/chole|chana/i), has({ to: SUN, delivered: true }))]);
add("indirect", "K02", "kya karna hai aaj?", FAM, [
  t("Anjali here. Tell Kamla to clean the terrace.", has({ to: KAM })),
  t("Kamla hoon. Aaj kya karna hai?", L, reply(/terrace|chhat|chat|गच्ची/i), has({ to: KAM, delivered: true }))]);
add("indirect", "K03", "आज काय करायचं?", FAM, [
  t("Rahul here. Tell Kamla to polish the silver for puja.", has({ to: KAM })),
  t("मी कमला. आज काय करायचं?", D, reply(/चांदी/), has({ to: KAM, delivered: true }))]);
add("indirect", "K04", "आज खाने में क्या बनाऊँ? with no message -> must not invent", SMALL, [
  t("मैं सुनीता हूँ। आज खाने में क्या बनाऊँ?", D, tool("get_messages"), count(0), not(/मैडम ने कहा|अंजली ने कहा|संदेश है/))]);
add("indirect", "K05", "Driver: kahan jaana hai?", FAM, [
  t("Rahul here. Tell Raju to take Aaji to the hospital at 11 for a checkup.", has({ to: RAJ })),
  t("Raju hoon, aaj kahan jaana hai?", L, reply(/hospital|aspatal/i, /11|gyarah/i), has({ to: RAJ, delivered: true }))]);
add("indirect", "K06", "Cook: kuch bola hai memsaab ne?", SMALL, [
  t("मी अंजली. सुनीताला सांग, आज भाकरी आणि पिठलं.", has({ to: SUN })),
  t("Memsaab ne kuch bola hai kya? Sunita hoon.", L, reply(/bhakri|bhakhri|bhakari|भाकरी/i, /pithl|besan|पिठल/i))]); // FIXER NOTE: R3 accept bhakari / pithalam / pithle spellings

/* ---------- L: long multi-detail ---------- */
add("long_detail", "L01", "Party menu with quantities", SMALL, [
  t("Anjali here. Tell Sunita: tomorrow 12 guests for lunch. Make 2 kg chicken biryani, 1 kg paneer butter masala, raita with 1 litre curd, 40 puris, and gulab jamun from the box in the fridge. Start by 10 am.", has({ to: SUN, text: [/12/, /2 ?kg|2 किलो/i, /40/, /10/] })),
  t("मैं सुनीता हूँ, कल के लिए क्या संदेश है?", D, reply(/12|बारह|१२/, /बिरयानी/, /2|दो|२/, /पनीर/, /रायता/, /40|चालीस|४०/, /पूरी|पुरी/, /गुलाब जामुन/, /10|दस|१०/))]);
add("long_detail", "L02", "Driver errands with times and places", FAM, [
  t("Rahul here. Tell Raju: at 9 drop Isha at Kothrud school, at 11 collect the medicines from Apollo pharmacy, at 4 pick up Aarav from cricket at Deccan Gymkhana, and fill CNG before that.", has({ to: RAJ })),
  t("Raju here, aaj ka kya plan hai?", reply(/9|nau/i, /Kothrud/i, /11|gyarah/i, /Apollo/i, /4|chaar/i, /Deccan/i, /CNG/i))]);
add("long_detail", "L03", "Marathi multi-task for maid", FAM, [
  t("मी अंजली. कमलाला सांग: आधी भांडी, मग हॉल आणि बेडरूम झाडून पुसून घे, वॉशिंग मशीनमधले कपडे वाळत घाल, आणि कुंड्यांना पाणी घाल. आज बारा वाजेपर्यंत संपव.", has({ to: KAM })),
  t("मी कमला. आज काय काय करायचं?", D, reply(/भांडी/, /हॉल/, /बेडरूम/, /कपडे/, /कुंड्या|झाड|रोप/, /बारा|12|१२/))]);
add("long_detail", "L04", "English recipe-like detail to Hindi cook, no invented items", SMALL, [
  t("Anjali here. Tell Sunita: dal with only half spoon salt, no green chilli, 4 rotis for Aaji soft ones, and rice only one cup.", has({ to: SUN })),
  t("मैं सुनीता, कोई संदेश?", D, reply(/नमक/, /मिर्च/, /4|चार|४/, /रोटी|रोटि/ /* FIXER NOTE: R3 accept रोटियां */, /चावल/, /एक|1|१/), not(/प्याज|आलू|पनीर/))]);
add("long_detail", "L05", "Phone numbers and amounts survive", FAM, [
  t("Rahul here. Tell Anjali the AC repair guy Salim will call from 98220 12345, the charge is 1800 rupees, pay him cash.", has({ to: ANJ, text: [/98220 ?12345/, /1800/] })),
  t("Anjali here, any message?", L, reply(/98220 ?12345|9 ?8 ?2 ?2 ?0/, /1800|1,800|eighteen hundred/i, /Salim/, /cash/i))]);
add("long_detail", "L06", "Hindi detailed to English kid", FAM, [
  t("मैं राहुल। आरव को बोलो: स्कूल बैग में स्विमिंग कॉस्ट्यूम, तौलिया और 50 रुपये रख ले, बस 7:15 पर आएगी।", has({ to: AAR })),
  t("Aarav here, what do I need to know?", L, reply(/swim/i, /towel/i, /50/, /7[:.]15|quarter past seven/i))]);

/* ---------- M: small talk ---------- */
add("smalltalk", "M01", "Greeting does not create message", FAM, [t("Hi TODO, good morning! How are you?", L, count(0), notool("leave_message"))]);
add("smalltalk", "M02", "Marathi chit-chat", FAM, [t("मी अंजली. आज खूप उकडतंय ना?", D, count(0))]);
add("smalltalk", "M03", "Talking ABOUT someone isn't a message", FAM, [t("Rahul here. Sunita makes the best biryani, doesn't she?", L, count(0), notool("leave_message"))]);
add("smalltalk", "M04", "Hindi: reporting, not asking to pass on", FAM, [t("मैं सुनीता हूँ। आज बहुत गर्मी है, मैंने खाना बना दिया है।", D, count(0))]);
add("smalltalk", "M05", "Question about a person, not a message", FAM, [t("Isha here. Is Raju coming today?", L, count(0), notool("leave_message"))]);
add("smalltalk", "M06", "Thank you after delivery doesn't create new message", SMALL, [
  t("Anjali here. Tell Sunita to make kheer.", has({ to: SUN })),
  t("सुनीता हूँ, संदेश?", D, reply(/खीर/)),
  t("ठीक है, धन्यवाद!", D, count(1))]);

/* ---------- N: the name ---------- */
add("name", "N01", "Are you a bot?", FAM, [t("Are you a bot?", L, reply(/TODO/))]);
add("name", "N02", "तुम कौन हो?", FAM, [t("तुम कौन हो?", D, reply(/TODO|टूडू|टुडू|टू डू/))]);
add("name", "N03", "Tu kon aahes? (romanised Marathi)", FAM, [t("Tu kon aahes?", reply(/TODO/i))]);
add("name", "N04", "Assistant framing from user", FAM, [t("Hey assistant, what can you do for this house?", L, reply(/TODO|message|list/i))]);

/* ---------- O: one person, two languages, switching across turns (page rebuilt 11:48:51 with langs[]) ---------- */
const BI = [{ name: "Anjali", role: "mother", langs: ["Marathi", "English"] }, { name: "Sunita", role: "cook", langs: ["Hindi", "Marathi"] },
  { name: "Raju", role: "driver", langs: ["Hindi", "English"] }];
add("bilingual", "O01", "Cook switches Hindi -> Marathi between asks", BI, [
  t("Anjali here. Tell Sunita to make methi paratha.", has({ to: SUN })),
  t("मैं सुनीता हूँ, कोई संदेश?", D, reply(/मेथी/)),
  t("मराठीत परत सांगा, मी सुनीता.", D, reply(/मेथी/), not(/है|बनाओ|बनाना/))]);
add("bilingual", "O02", "Mother leaves in English then follows up in Marathi", BI, [
  t("Anjali here. Tell Raju to pick me up at 6 from office.", L, has({ to: RAJ })),
  t("आणि त्याला सांग, येताना भाजी घेऊन ये.", D, tool("leave_message")),
  t("Raju here, any message?", L, reply(/6|six/i, /vegetable|sabzi|bhaji/i))]);
add("bilingual", "O03", "Driver asks in English, then Hindi, reply follows current language", BI, [
  t("मी अंजली. राजूला सांग उद्या सुट्टी.", has({ to: RAJ })),
  t("Raju here. Message for me?", L, any(/off|holiday|leave/i)),
  t("हिंदी में बोलो", D, reply(/छुट्टी/))]);
add("bilingual", "O04", "Bilingual sender's message delivered in recipient's current language, not roster default", BI, [
  t("मैं सुनीता हूँ। अंजली दीदी को बोलना, गैस वाला आया था।", has({ from: SUN, to: ANJ })),
  t("Anjali here, anything for me?", L, reply(/gas/i))]);
add("bilingual", "O05", "add_person with two languages", FAM, [
  t("Anjali here. This is Meena, our new cook, she speaks Marathi and Hindi.", tool("add_person")),
  t("मी मीना. माझ्यासाठी काही?", D, count(0))]);
export const SCENARIOS = S;
