
import google.generativeai as genai
import traceback

# Mock the available functions
available_functions = [
    {
        "name": "analyze_customer_sentiment",
        "description": "Analyze customer sentiment from conversations",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer's unique identifier"
                },
                "messages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Recent messages to analyze"
                }
            },
            "required": ["customer_id", "messages"]
        }
    }
]

def _convert_schema_to_proto(schema_dict):
    """Recursively convert JSON schema dict to genai.protos.Schema"""
    type_str = schema_dict.get("type", "STRING").upper()
    
    type_map = {
        "STRING": genai.protos.Type.STRING,
        "INTEGER": genai.protos.Type.INTEGER,
        "NUMBER": genai.protos.Type.NUMBER,
        "BOOLEAN": genai.protos.Type.BOOLEAN,
        "ARRAY": genai.protos.Type.ARRAY,
        "OBJECT": genai.protos.Type.OBJECT,
    }
    gemini_type = type_map.get(type_str, genai.protos.Type.STRING)
    
    # Base kwargs
    schema_kwargs = {
        "type_": gemini_type,
        "description": schema_dict.get("description", ""),
        # "nullable": schema_dict.get("nullable", False) # Removed as per my last fix
    }
    
    # Hande Enum
    if "enum" in schema_dict:
        schema_kwargs["enum"] = schema_dict["enum"]
        
    # Handle Array items
    if gemini_type == genai.protos.Type.ARRAY and "items" in schema_dict:
        schema_kwargs["items"] = _convert_schema_to_proto(schema_dict["items"])
        
    # Handle Object properties
    if gemini_type == genai.protos.Type.OBJECT and "properties" in schema_dict:
        props = {}
        for k, v in schema_dict["properties"].items():
            props[k] = _convert_schema_to_proto(v)
        schema_kwargs["properties"] = props
        if "required" in schema_dict:
            schema_kwargs["required"] = schema_dict["required"]

    print(f"DEBUG: Building Schema for type={type_str}, kwargs={schema_kwargs.keys()}")
    return genai.protos.Schema(**schema_kwargs)

try:
    print("Attempting to build tools...")
    tool_declarations = []
    for func in available_functions:
        print(f"Processing {func['name']}...")
        params_dict = func.get("parameters", {})
        if params_dict.get("type", "").upper() != "OBJECT":
            params_dict["type"] = "OBJECT"
            
        proto_schema = _convert_schema_to_proto(params_dict)
        
        func_decl = genai.protos.FunctionDeclaration(
            name=func["name"],
            description=func.get("description", ""),
            parameters=proto_schema
        )
        tool_declarations.append(func_decl)
    
    tools = [genai.protos.Tool(function_declarations=tool_declarations)]
    print("✅ SUCCESS: Tools built successfully!")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    traceback.print_exc()
