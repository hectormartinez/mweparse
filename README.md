# mweparse
Data exporter for joint lexical-dependency prediction.

42	personnel	personnel	N	NC	g=m|n=s|s=c|mwehead=NC	41	obj.p	41	obj.p
43	technique	technique	A	ADJ	n=s|s=qual|component=y	42	mod_rmwe_NC	42	mod_rmwe_NC

(1) For fixed MWEs, labels are in the form "mwe_POS" where POS is the part-of-speech tag of the MWE.
 (2) For non-fixed MWEs, labels are in the form "FUNC_rmwe_POS" where 
        * FUNC is a syntactic function label (syntax dimension)
        * POS is the POS of the MWE
        * rmwe stands for "regular MWE" 

