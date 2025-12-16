import sys
import warnings

print("Verifying warnings...")
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    # Simulate app imports
    try:
        from google.protobuf import symbol_database
    except ImportError:
        pass
        
    import mediapipe as mp
    import cv2
    
    # Check for specific warnings
    found_protobuf = False
    found_secure = False
    
    for warning in w:
        msg = str(warning.message)
        print(f"WARNING: {msg}")
        if "SymbolDatabase.GetPrototype() is deprecated" in msg:
            found_protobuf = True
            
    if found_protobuf:
        print("FAIL: Protobuf warning still present.")
    else:
        print("PASS: Protobuf warning gone.")
