"""What whoever designs with these packages is told before reading their nodes.

A node says what it is; a kind says what its nodes take. Neither says when to reach for one, or
what to do where the knowledge stops (a saw whose maker prints no cut, a length that cannot be
measured). That is said here, as nodes of kind guidance under the branch `guidance`: payload text,
and the link about to the nodes it speaks of, so a guidance that outlives what it speaks of is
refused by a rule instead of being read. A reader (a connector, a skill) gives its assistant every
guidance of the tree it works in, and writes none of its own: a package that adds a shop, a tool or
a rule adds what must be said of it.
"""
from __future__ import annotations

from quern.tree import Node

GUIDANCE = "guidance"


def say(id_: str, name: str, text: str, *about: str) -> Node:
    """One guidance: `name` is what it is about, in a few words; `text` its sentences; `about` the
    paths of the nodes it speaks of."""
    return Node(id=id_, kind="guidance", name=name, payload={"text": " ".join(text.split())},
                links={"about": list(about)} if about else {})


def branch(*nodes: Node) -> Node:
    return Node(id=GUIDANCE, kind="", children=list(nodes))


def guidance() -> Node:
    """furniture-design's own guidance: how a piece is written, bought, cut and measured."""
    return branch(
        say("a-piece-is-data", "How a piece is written", """
            A piece is data, never code. Its id is the piece's name. The piece states its dimensions once, as
            params (hauteur, largeur, profondeur, ...), and each part's shape size, transform translate and cuts
            are numbers or expressions over params in scope - the part's own, then the piece's:
            "largeur - 2 * cote", "hauteur - plateau". Change a dimension where it is stated and every part
            written over it follows; never copy a computed number into a part. Its parts, joints and loads are
            its children, and links name nodes by path ("pieces/<id>/<part>", and the materials, connectors,
            tools, requirements and sources of the knowledge beside it). The payload carries version, authors,
            date and steps, and never a description: what a description would say is an entry of the piece's
            ledger. Write from what the kinds and rules define, not only from a piece you read: a kind says
            what its nodes are and the params and links they take, a rule what is checked and the calculations
            it uses, and the knowledge holds the materials, requirements, sources, connectors and tools a
            piece links to, by the path a link names. A question the rules cannot answer is not answered by a
            calculation inside the piece: say so, and say what knowledge or rule is lacking."""),
        say("assemblies", "Parts that go together", """
            Parts that go together as one thing (a door, a rail, a drawer) go under a node of kind assembly (an
            id, a name, its parts as children), beneath the piece or another assembly, to any depth. An assembly
            places and weighs nothing: its parts keep their transform relative to the piece and read its params
            as before. A link to a part under one names it through its assemblies
            ("pieces/<id>/<assembly>/<part>"); a step's add names the part's id as before. The 3D view lists the
            piece by its assemblies: the person opens one to see it alone, a long thin one from its end."""),
        say("profiles", "A profile is one part", """
            A profile (an angle, a channel, a tube) is one part, never one part per face: its box is the whole
            it fits in, and its payload section is the outline of what it is across its length, points [a, b]
            in mm from its minimum corner along the two shorter sides of its box in the order of the axes (a
            profile lying along x gives [y, z]). A 12 x 12 x 1 channel open upwards along x:
            [[0,0],[12,0],[12,12],[11,12],[11,1],[1,1],[1,12],[0,12]]."""),
        say("numbers-carry-their-source", "Where a number comes from", """
            Numbers carry their source: a size somebody chose is a design target, a measured one is "measured"
            with its tolerance, and a published one names where it is published. Never invent a source; say
            what is missing instead."""),
        say("lengths-taken-where-they-go", "A part that fits between two surfaces", """
            A part that fits between two surfaces of the room (a rail from wall to wall, a door from rail to
            rail) has its length taken where it goes, not measured: link it made_with tools/pinch-sticks, whose
            method says how. Do not ask the person to measure that length; its param is an estimate read off
            the photos ("inferred"), there to draw the piece, and say so.""",
            "tools/pinch-sticks"),
        say("boards-bought", "The boards a piece is bought as", """
            The boards bought are the piece's payload stock, a list of {material, length, width} in mm (length
            along the grain; optional ref and note), the material as a part's uses names it: when the person
            says which board they buy (a size seen in the store, one they have), it goes there, not only in the
            ledger. A material the piece names no board of is laid on the sheets its shop lists of it, else
            listed with its parts, a board to choose."""),
        say("the-saw-that-cuts-a-part", "The saw a part is cut with", """
            The saw that cuts a part out of its board is the part's link sawn_with, one of the saws among the
            tools, each with the cut of its blade (kerf) and the thickest board it cuts (max_cut_depth) as its
            maker prints them: the cutting sheet leaves that saw's cut between the parts and says whose. When
            the person says which saw they cut with, it goes there. A saw whose maker prints no cut is refused
            by a rule: ask the person to measure the width of a cut their saw makes, and state it as kerf
            ("measured", with its tolerance) on a tool of the piece's own. A part that names no saw is laid
            with a default cut, which the sheet says. The parts of a person's pieces are cut and made with the
            tools that person has, a shop's cutting service, or the blade or measured cut said here."""),
        say("profiles-sawn-by-hand", "Sawing a profile to length", """
            A profile is sawn to length by hand as tools/hacksaw-on-profile says; no maker prints the cut of a
            hacksaw, so ask the person to measure one and state it as kerf on a tool of the piece's own that
            follows tools/hacksaw-on-profile. An aluminium profile may also be cut with an angle grinder and an
            aluminium disc (the method tools/angle-grinder); no maker of PVC profiles names a grinder for one,
            so saw it.""",
            "tools/hacksaw-on-profile", "tools/angle-grinder"),
        say("what-the-knowledge-lacks", "A tool, material or source the knowledge lacks", """
            A tool, material or source the knowledge lacks is written as the packages write theirs: find the
            maker's documents (manual, datasheet, product page), write the source (payload publisher, url,
            fetched, licence, authority; a copyrighted one's clauses carry their locator and the values
            printed, no quote), and the tool or material on the kinds, each param derived_from the clause that
            prints it; an installed node of the same kind shows how. A tool's model is payload model
            {"parts": [solid, ...]}, mm, Z up, built from the maker's dimensions and photos, to hold against
            the maker's photos once drawn. A value no document prints is not filled in."""),
        say("how-far-a-part-may-sag", "How far a seat or shelf may sag", """
            How far a seat or shelf may sag is not one number: the sources hold every published limit, each a
            clause with what it is written for; none is written for a seat, so a piece authors its own
            requirement (measure longtime_sag, param limit in mm) per the clause it follows and links it from a
            part as sag_limit. A quality the person wants kept is held only when it is a requirement the piece
            links: a variation that sags, weighs or tips more is only flagged by the rules when a requirement
            says how much is too much. A connector lists in its payload tested_elsewhere the tests of other
            sizes or materials that are not its ratings."""),
        say("grooves-are-drawn", "The step that cuts a joint's grooves", """
            The assembly instructions draw how each joint's grooves are cut, with no sentence: a preparation
            step that lists in joints the joints whose grooves it cuts gets pages of their own, the machine's
            settings drawn on it, then per kind of joint the two parts marked across the joint from their
            reference face, the machine on each part drawn from its model, and the jig drilling the access
            holes. List there every joint whose grooves the step cuts."""),
        say("one-language", "The language a piece is made in", """
            A piece is made in one language. Write its ledger's entries, and the text in the piece (names,
            steps, notes), in that language, whatever language the person writes in; the notes' headings, the
            plans, the assembly instructions and the rules' findings come out in it. No programmer's words: the
            documents are for the people who build."""),
    )
