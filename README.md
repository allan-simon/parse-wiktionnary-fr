# parse-wiktionnary-fr
a python3 script which extract and organize information from a french wiktionnary dump

You can get a dump here 

https://dumps.wikimedia.org/frwiktionary/

## Note on the code and dump structure

Currently the code follow a state-machine-like architecture
Even if the dump is an XML file, it actually only has the name by that I mean
that an XML parser will not permit you to extract any useful information.

  * Fortunately opening `<page>` tags are on a line alone
  * Then you can look for the `<title>` tag to get the word itself:
    * if it's starts with a predefined set of `XXXX:` it's actually a meta page (or template page)
      and you can ignore the full page
  * If it's an actual word then you can look for the real wiktionary content, the one in `<text xml:space="preserve">`
    but as what you will find inside (i.e mediawiki syntax) can not be found elsewhere, you do not need to specifically
    look for this tag, and can directly goes to the next step
  * You look for the language, it starts with `== {{langue|fr}} ==` , if it's an other `== {{langue|XX}} ==` you can skip all lines until the next `langue` section (and so on)
  * TODO


### Example

```
        <id>413</id>
      </contributor>
      <comment>-espace</comment>
      <model>wikitext</model>
      <format>text/x-wiki</format>
      <text xml:space="preserve">$1 modifications mineures | $2 robots | $3 utilisateurs enregistrés&lt;!-- | $4 patrolled edits --&gt; | $5 mes contributions</text>
      <sha1>jtng03p6jsoijbw6cx0bz90hp9qa4pa</sha1>
    </revision>
  </page>
  <page>
    <title>MediaWiki:Sitetitle</title>
    <ns>8</ns>
    <id>12</id>
    <revision>
      <id>403956</id>
      <parentid>33016</parentid>
      <timestamp>2006-02-13T09:08:31Z</timestamp>
      <contributor>
        <username>Kipmaster</username>
        <id>214</id>
      </contributor>
      <comment>changement de titre pour meilleur référencement dans les moteurs de recherche</comment>
      <model>wikitext</model>
      <format>text/x-wiki</format>
      <text xml:space="preserve">Wiktionnaire : dictionnaire libre et universel</text>
      <sha1>40helna9646ffk0utvwm8bkdlzi1eck</sha1>
    </revision>
  </page>
  <page>
    <title>lire</title>
    <ns>0</ns>
    <id>13</id>
    <revision>
      <id>20318937</id>
      <parentid>19897043</parentid>
      <timestamp>2015-09-12T10:28:18Z</timestamp>
      <contributor>
        <username>JAnDbot</username>
        <id>65802</id>
      </contributor>
      <minor />
      <comment>r2.7.3) (robot Ajoute : [[scn:lire]]</comment>
      <model>wikitext</model>
      <format>text/x-wiki</format>
      <text xml:space="preserve">{{voir|Lire|Liré}}

== {{langue|fr}} ==
=== {{S|étymologie}} ===
: ([[#fr-verb|Verbe]]) Du {{étyl|la|fr|mot=lego|dif=lĕgĕre|sens=''id.''}}.
: ([[#fr-nom|Nom]]) De l’{{étyl|it|fr|mot=lira}}, du latin ''[[libra]]'' (« [[livre]] » : le poids).

=== {{S|verbe|fr}} ===
'''lire''' {{pron|liʁ|fr}} {{conjugaison|fr|grp=3}}
# [[interpréter|Interpréter]] des [[information]]s écrites sous forme de [[mot]]s ou de [[dessin]]s sur un [[support]].
#* ''On '''lit''' ce livre absolument comme au bord de la cascade on entendrait, rêveur, le gazouillement des eaux.'' {{source|{{w|Jules Michelet}}, ''Du prêtre, de la femme, de la famille'', 3{{e}} éd., Hachette &amp; Paulin, 1845, p.133}}
#* ''[…]; je me souviens d’'''avoir lu''' autrefois, dans un manuel de Paul Bert, que le principe fondamental de la morale s’appuie sur les enseigne­ments de Zoroastre et sur la Constitution de l’an III ; […].'' {{source|{{w|Georges Sorel}}, ''Réflexions sur la violence'', Chap.VII, ''La morale des producteurs'', 1908, p.315}}
#* ''[…], mais vous comprenez bien qu’on ne donne pas une égale attention à tout ce qu’on '''lit''' ou qu’on parcourt dans les colonnes des journaux […].'' {{source|{{w|Louis Pergaud}}, ''[[s:Un point d’histoire|Un point d’histoire]]'', dans ''{{w|Les Rustiques, nouvelles villageoises}}'', 1921}}
#* '' Il était célèbre par une obstination admirable à apprendre à écrire et à '''lire''' ; le résultat ne fut pas étonnant ; il faut croire qu’il est bien difficile d’apprendre à '''lire''' ; […].'' {{source|[[w:Alain (philosophe)|Alain]], ''Souvenirs de guerre'', p.75, Hartmann, 1937}}
#* ''Mais '''lire''', c’est surtout entrer en soi-même, apprendre à se considérer comme un monde de signes, de messages codés, de rébus.'' {{source|Philippe Sollers, ''Éloge de l’infini'', Gallimard, p. 619}}
# [[suivre|Suivre]] des [[yeux]] ce qui est [[écrit]] ou [[imprimer|imprimé]], [[avec]] la [[connaissance]] des sons que les [[lettre]]s [[figurent]]; [[soit]] en ne [[proférer|proférant]] pas les mots, [[être|soit]] en les proférant à [[haut]]e [[voix]].
#* ''Ce qui m’étonne, c’est que le propriétaire dudit bouquin ne semble pas le '''lire''' de droite à gauche. Est-ce qu’il ne serait pas imprimé en caractères chinois ?'' {{source|{{Citation/Jules Verne/Claudius Bombarnac/1892|6}}}}
#* ''Il s’est fatigué la vue à '''lire''' de vieux manuscrits.''
#* ''Une écriture difficile à '''lire'''.''
# [[prendre connaissance|Prendre connaissance]] et [[comprendre]] un texte écrit.
#* ''Il est de jeunes écrivains qui ne '''lisent''' pas Hugo. C’est pourquoi ils ont tant de certitudes heureuses et atteignent promptement au talent.'' {{source|{{Citation/Victor Méric/Les Compagnons de l’Escopette/1930|67}}}}
# [[comprendre|Comprendre]] ce qui est écrit ou imprimé dans une [[langue]] [[étranger|étrangère]].
#* ''Il ne parle pas l’anglais, mais il le '''lit''' avec assez de facilité.''
# {{musique|fr}} {{analogie|fr}} Parcourir des yeux une musique notée, avec la connaissance des sons que les notes figurent et des diverses modifications que ces sons doivent recevoir.
#* '''''Lire''' une partition''
# [[prononcer|Prononcer]] à haute [[voix]], avec l’[[intonation]] voulue, ce qui est écrit ou imprimé.
#* ''Il '''lit''' bien, il '''lit''' mal.''
#* ''Il '''lit''' distinctement.''
#* ''Il ne sait pas '''lire'''.''
#* ''Il nous a '''lu''' un long discours.''
#* ''Je vais vous '''lire''' mes vers.''
#* ''Ce prince avait l’habitude de se faire '''lire''' quelque bon livre pendant ses repas.''
# S’[[instruire]], s’[[amuser]], s’[[informer]], etc. par la lecture.
#* '''''Lire''' un volume de vers, un roman, un billet, une lettre, la messe, une dépêche chiffrée.''
#* {{absolument}} ''Il passe son temps à '''lire'''.''
#* {{figuré|fr}} ''C’est un ouvrage qu’on ne peut '''lire''','' se dit d’un ouvrage ennuyeux, ou mal écrit, ou surtout licencieux.
#* {{figuré|fr}} et {{familier|fr}} ''Ce livre, cet ouvrage se laisse '''lire''','' On le lit sans fatigue, sans ennui.
# Se dit encore en parlant de quelque [[livre]] qu’un [[professeur]] [[expliquer|explique]] ou fait expliquer à ses [[auditeur]]s et qu’il prend pour [[sujet]] des [[leçon]]s qu’il [[leur]] [[donne]].
#* ''Notre professeur nous '''lisait''' Homère.''
# {{figuré|fr}} [[pénétrer|Pénétrer]] [[quelque chose]] d’[[obscur]] ou de [[cacher|caché]].
#* ''L’ivresse se '''lisait''' dans ses yeux, une ivresse crâne et satisfaite qui lui arrachait quelquefois de gros rires.'' {{source|{{Citation/Francis Carco/Messieurs les vrais de vrai/1927}}}}
#* ''A quoi songes-tu donc ? s’informa la maîtresse du logis, surprise de l’inattention qu’elle '''lisait''' dans les yeux de l’artiste. Tu n’as pas de contrariétés.'' {{source|{{Citation/Francis Carco/L’Homme de minuit/1938}}}}
#* '''''Lire''' dans la pensée, dans le cœur, dans les yeux de quelqu’un.''
#* ''Je '''lis''' sur votre visage que vous êtes mécontent.''
#* '''''Lire''' dans les astres, dans l’avenir.''

==== {{S|dérivés}} ====
* [[entrelire]]
* [[lire-écrire]]
* [[relire]]

==== {{S|expressions}} ====
* [[lire sur les lèvres]]
* [[lire entre les lignes]]
* [[lire en diagonale]]

==== {{S|traductions}} ====
{{trad-début|Interpréter des informations écrites.}}
* {{T|de}} : {{trad+|de|lesen}}
* {{T|en}} : {{trad+|en|read}}
* {{T|ca}} : {{trad+|ca|llegir}}
* {{T|zh}} : {{trad+|zh|读|tr=dú|tradi=讀}}
* {{T|ko}} : {{trad+|ko|읽다|tr=ikda}}
* {{T|es}} : {{trad+|es|leer}}
* {{T|it}} : {{trad+|it|leggere}}
* {{T|ja}} : {{trad+|ja|読む|tr=yomu}}
* {{T|mk}} : {{trad-|mk|чита|tr=tschita}}
* {{T|plodarisch}} : {{trad--|plodarisch|lesn}}
* {{T|pt}} : {{trad+|pt|ler}}
{{trad-fin}}

{{trad-début|Suivre des yeux ce qui est écrit ou imprimé.}}
* {{T|de}} : {{trad+|de|lesen}}
* {{T|en}} : {{trad+|en|read}}
* {{T|ca}} : {{trad+|ca|llegir}}
* {{T|es}} : {{trad+|es|leer}}
* {{T|it}} : {{trad+|it|leggere}}
* {{T|kk}} : {{trad+|kk|оқу|tr=oquw}}
* {{T|mk}} : {{trad-|mk|чита|tr=tschita}}
* {{T|plodarisch}} : {{trad--|plodarisch|lesn}}
{{trad-fin}}

{{trad-début|Prendre connaissance et comprendre un texte écrit.}}
* {{T|de}} : {{trad+|de|lesen}}
* {{T|en}} : {{trad+|en|read}}
* {{T|ca}} : {{trad+|ca|llegir}}
* {{T|es}} : {{trad+|es|leer}}
* {{T|it}} : {{trad+|it|leggere}}
{{trad-fin}}

{{trad-début|Comprendre ce qui est écrit ou imprimé dans une langue étrangère.}}
* {{T|de}} : {{trad+|de|lesen}}
* {{T|en}} : {{trad+|en|read}}
* {{T|es}} : {{trad+|es|leer}}
* {{T|it}} : {{trad+|it|leggere}}
* {{T|mk}} : {{trad-|mk|чита|tr=tschita}}
{{trad-fin}}

{{trad-début|(Musique) (Par analogie) Parcourir des yeux une musique notée.}}
* {{T|de}} : {{trad+|de|lesen}}
* {{T|en}} : {{trad+|en|read}}
* {{T|ca}} : {{trad+|ca|llegir}}
* {{T|es}} : {{trad+|es|leer}}
* {{T|it}} : {{trad+|it|leggere}}
{{trad-fin}}

{{trad-début|Prononcer à haute voix, avec l’intonation voulue, ce qui est écrit ou imprimé.}}
* {{T|de}} : {{trad+|de|lesen}}
* {{T|en}} : {{trad+|en|read}}
* {{T|ca}} : {{trad+|ca|llegir}}
* {{T|es}} : {{trad+|es|leer}}
* {{T|it}} : {{trad+|it|leggere}}
* {{T|mk}} : {{trad-|mk|чита|tr=tschita}}
{{trad-fin}}

{{trad-début|S’instruire, s’amuser, s’informer, etc. par la lecture.}}
* {{T|de}} : {{trad+|de|lesen}}
* {{T|en}} : {{trad+|en|read}}
{{trad-fin}}

{{trad-début|Expliquer un livre pris pour sujet de leçons.}}
* {{T|de}} : {{trad+|de|lesen}}
* {{T|en}} : {{trad+|en|read}}
{{trad-fin}}

{{trad-début|(Figuré) Pénétrer quelque chose d’obscur ou de caché.}}
* {{T|de}} : {{trad+|de|lesen}}
* {{T|en}} : {{trad+|en|read}}
* {{T|ca}} : {{trad+|ca|llegir}}
{{trad-fin}}

===== {{S|traductions à trier}} =====
{{trad-début}}
* {{T|ab}} : {{trad--|ab|аҧхьара}}
* {{T|ady}} : {{trad--|ady|еджэн}}
* {{T|bs}} : {{trad-|bs|čitati}}
{{trad-fin}}

=== {{S|nom|fr}} ===
{{fr-rég|liʁ}}
'''lire''' {{pron|liʁ|fr}} {{f}}
# [[monnaie|Monnaie]] utilisée en [[Italie]] avant l’usage de l’[[euro]].
#* ''Un euro vaut environ 1936 '''lires'''.''

=== {{S|prononciation}} ===
* {{écouter|lang=fr|France &lt;!-- précisez svp la ville ou la région --&gt;|liʁ|audio=Fr-lire.ogg}}

==== {{S|homophones}} ====
* [[lyre]]

=== {{S|anagrammes}} ===
* [[riel]]
* [[lier]]

=== {{S|voir aussi}} ===
* {{WP}}

[[Catégorie:Monnaies en français]]

== {{langue|fro}} ==
=== {{S|étymologie}} ===
: Du {{étyl|la|fro|mot=lyra}}.

=== {{S|nom|fro}} ===
'''lire''' {{pron|liʁ|fro}}
# [[lyre#fr|Lyre]].
#* ''De vièle sot et de rote,&lt;br&gt;De '''lire''' et de satérion,&lt;br&gt;De harpe sot et de choron,&lt;br&gt;(…)'' {{source|{{w|Wace}}, ''Roman de Brut'', 1155}}

[[Catégorie:Instruments de musique en ancien français]]

== {{langue|af}} ==
=== {{S|étymologie}} ===
: {{ébauche-étym|af}}

=== {{S|nom|af}} ===
'''lire''' {{pron||af}}
# [[lire#fr-nom|Lire]].

[[ar:lire]]
[[ca:lire]]
[[chr:lire]]
```
