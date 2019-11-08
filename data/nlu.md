## intent:bot_challenge
- sei un bot?
- sei un umano?
- sto parlado con un bot?
- sto parlado con un umano?

## intent:goodbye
- arrivederci
- arrivederla
- ci si rivede
- a presto
- ci si risente
- ci risentiamo

## intent:greet
- ciao
- salve
- buongiorno
- buonpomeriggio
- buonasera


## intent:query_knowledge_attribute_of
- mi puoi dare il [numero](telefono) del dottor [FRANCO BONGIANINO](medico) ?
- conosci l' [indirizzo](attribute:indirizzo) di [questo](mention) ?
- che [attività](attribute:attivita) fanno [loro](mention) ?
- sai che [attività](attribute:attivita) fa l' [ultimo](mention:LAST) ?
- qual'è l' [email](attribute) del dottor [ALESSANDRO FILIPPI](medico) ?
- mi puoi dire gli [indirizzi](attribute:indirizzo) degli ambulatori a [TORINO](comune) ?
- mi serve i [numeri](attribute:telefono) dei medici a [GOZZANO](comune)
- mi puoi dire il [numero](attribute:telefono) di [questo dottore](mention) ?
- in che [città](attribute:comune) opera [lui](mention) ?
- per favore elencami alcuni [ambulatori](attribute:ambulatorio) a [NEVIGLIE](comune) per me
- dimmi il [numero civico](attribute:civico) dello studio del dottor [FRANCO BONGIANINO](medico)
- dimmi l' [indirizzo](attribute:indirizzo) dello studio del dottor [ROBERTO POLETTI](medico)
- l' [ultimo](mention:LAST) risiede in quale [via](attribute:indirizzo)?
- il [secondo](mention:2) sta in quale [via](attribute:indirizzo)?
- qual'è il [numero](attribute:telefono) del [secondo](mention:2) dottore?
- mi serve l'[email](attribute) del [primo](mention:1)
- il [terzo](mention:3) in che [città](attribute:comune) ha l'ambulatorio ?
- da che [anno])(attribute:Data_inizio_attivita) lavora il dottor [ROBERTO POLETTI](medico)?
- mi serve il [cap](attribute:cap) dell'ambulatorio [MONTALDO ROERO](ambulatorio)
- mi diresti il [CAP](attribute:cap) dell'ambulatorio [MONTALDO ROERO](ambulatorio)
- conosci l'[indirizzo](attribute:indirizzo) di [questo](mention) ?
- conosci il [numero](attribute:telefono) di [questo](mention) ?
- mi puoi dare l' [email](attribute) dell'[ultimo](mention:LAST)?
- mi puoi dire il [telefono](attribute:telefono) del [primo](mention:1)?
- in che [città](attribute:comune) opera il [primo](mention:1)?
- dov'è lo [studio](attribute:comune) del dottor [ROBERTO POLETTI](medico)?
- dimmi il [telefono](attribute:telefono) del dottor [ROBERTO POLETTI](medico)
- mi puoi dare l'[e-mail](attribute:email) del dottor [FLAVIO POLA](medico) ?

## intent:query_knowledge_list
- che [medico](object_type) mi consiglieresti  a [NOVARA](comune)?
- elencami alcuni [medici](object_type:medico) a [MERANA](comune)
- mi puoi nominare alcuni [medici](object_type:medico) per favore?
- mi puoi mostrare alcuni [medici](object_type:medico) a [PARETO](comune) ?
- elencami dei [medici](object_type:medico) che operano nel distretto [5](distretto)
- quale [dottoressa](object_type:medico) ha lo studio a [VERCELLI](comune) ?
- conosci anche alcuni [medici](object_type:medico) in [via nizza](indirizzo:VIA NIZZA) a [CARAGLIO](comune) ?
- cerco gli [orari](object_type:orario) dell'ambulatorio a [CUNEO](comune) 
- cerco gli [ambulatori](object_type:ambulatorio) che sono aperti dalle [10:00](ora_inizio)
- che [medici](object_type:medico) conosci a [DOMODOSSOLA](comune) ?
- nominami alcuni [dottori](object_type:medico) ad [ASTI](comune)
- che [medici](object_type:medico) ci sono a [SCOPELLO](comune)
- che [medici](object_type:medico) mi consiglieresti a [OCCIMIANO](comune)?
- che [medici](object_type:medico) miconsiglieresti a [CINZANO](comune)?
- mi puoi elencare alcuni [medici](object_type:medico) che operano fino alle  [18:00](ora_fine)?
- mi puoi dire gli [ambulatori](object_type:ambulatorio) che operano a [TORINO](comune)?
- mi puoi dire gli [orari](object_type:orario) che svolge il dr [BUONANIMA](cognome)?
- quale [dottoressa](object_type:medico) ha lo studio a [CASTIGLIONE FALLETTO](comune)?

## synonym:1
- primo

## synonym:2
- secondo

## synonym:3
- terzo

## synonym:attivita
- attività
- attivita

## synonym:cap
- cap
- CAP

## synonym:ambulatorio
- ambulatori

## synonym:comune
- città
- studio
- comune

## synonym:email
- email
- e-mail

## synonym:indirizzo
- indirizzo
- indirizzi
- via

## synonym:LAST
- ultimo

## synonym:civico
- numero civico

## synonym:telefono
- numero
- numeri
- telefono
- cellulare

## synonym:medico
- medici
- dottoressa
- dottore
- dottor
- dr
- medici

## lookup:cognome
  data/lookup_Cognome.txt

## lookup:nome
  data/lookup_Nome.txt
