from homebot.face import reading as R
P = [
 "My cat has been missing since Sunday. We put up posters. I really hope she comes back.",
 "The interview went well and then they offered me the job! I start Monday.",
 "I was so nervous about the recital, so I practised all night. It went perfectly!",
 "We went to the beach. The kids built a huge sandcastle. Then the waves washed it away and Riya cried.",
 "Aaj office mein bahut kaam tha. Boss ne daanta bhi. Ab bas sona hai.",
 "Grandpa fell in the bathroom. He's okay now, thankfully. The doctor said rest.",
 "I baked a cake for Amma. It came out burnt. But she ate it anyway and smiled.",
 "The traffic was terrible because of the rain. I missed my train. Now I'm just tired.",
 "Guess what? I got the scholarship! I can't believe it.",
 "My brother broke my headphones. He didn't even say sorry. I'm so annoyed.",
 "We lost the match. Coach said we played well though. Still feels bad.",
 "Mala aaj khup chhan vatla. Mitra bhetle. Pan ghari aalyavar kantala aala.",
]
for p in P:
    print([ (b[0], b[3]) for b in R.read_beats(p, model=False)], "|", p[:60])
