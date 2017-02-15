"""
This module contains some configuration variable for the system.

"""
RABBITMQ_SERVER_IP = 'localhost'

"""
This variable is the blueprint for the micro-services system.
"""
ARCHITECTURE = {

    # Tag miners to spawn, and how many

    "tag_miners": [
        {
            "tag": "cinema",
            "miners": 1
        },
        {
            "tag": "music",
            "miners": 1
        },
        {
            "tag": "events",
            "miners": 1
        },
        {
            "tag": "food",
            "miners": 1
        }
    ],

    # Assemblers to spawn, and their queue names

    "vector_assemblers": [
        {
            "queue": "assembly_queue_1"
        },
        {
            "queue": "assembly_queue_2"
        }
    ]
}
