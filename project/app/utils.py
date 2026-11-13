def normalize_skill(skill):
    skill = skill.strip().lower()

    aliases = {
        # C
        "c programming": "c",
        "c language": "c",
        "c lang": "c",

        # C++
        "cpp": "c++",
        "c plus plus": "c++",
        "c++ programming": "c++",

        # JavaScript
        "js": "javascript",
        "java script": "javascript",

        # AWS
        "amazon web services": "aws",
        "amazon aws": "aws",

        # SQL
        "structured query language": "sql",

        # Docker
        "docker container": "docker",
    }

    return aliases.get(skill, skill)
