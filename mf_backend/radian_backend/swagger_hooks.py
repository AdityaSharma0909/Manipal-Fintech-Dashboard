def remove_swagger_security(result, generator, request, public):
    print("====== SWAGGER HOOK CALLED ======")
    if 'security' in result:
        result['security'].clear()
    
    if 'components' in result and 'securitySchemes' in result['components']:
        result['components']['securitySchemes'].clear()
    
    # Also strip security from all paths
    if 'paths' in result:
        for path in result['paths'].values():
            for method in path.values():
                if isinstance(method, dict) and 'security' in method:
                    method['security'].clear()
                    
    return result
