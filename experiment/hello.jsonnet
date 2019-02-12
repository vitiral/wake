// regular definition
local parentName = "bob";

local create_person(name, title) = {
    name: name,
    title: title,
    greeting: title + " " + name,

    children: [],
    get_child(s, name):: create_person(name, s.title + " Jr."),
};

local bob = create_person(parentName, "Baron");

local bob_family = bob + {
    children: [
        bob.get_child(bob, "Joe"),
        bob.get_child(bob, "Sally"),
    ]
};

bob_family
