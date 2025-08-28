def test_function():
    try:
        x = 1/0
    except Exception as e:
        import traceback
        print("Error occurred:")
        print(str(e))
        print("\nTraceback:")
        print(traceback.format_exc())

test_function()

