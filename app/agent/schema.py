tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web_sync",
            "description": "Searches the web and returns a list of relevant URLs for a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": [
                    "query",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url_sync",
            "description": "Fetches HTML content from a URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                },
                "required": [
                    "url",
                ],
            },
        },
    },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "read_file",
    #         "description": "Reads text content from a file",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "path": {"type": "string"},
    #             },
    #             "required": ["path", ]
    #         }
    #     }
    # },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "write_file",
    #         "description": "Writes text content to a file",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "path": {"type": "string"},
    #                 "content": {"type": "string"},
    #             },
    #             "required": ["path", "content",]
    #         }
    #     }
    # }
]
