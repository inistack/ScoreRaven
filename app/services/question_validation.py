
class QuestionValidationError(Exception):
    pass


def validate_question_options(question_type, options_data):
    
    if question_type == 'written':
        if options_data:
            raise QuestionValidationError("Written questions cannot have options.")
        return
    
    if not options_data or len(options_data) < 2:
        raise QuestionValidationError("At least two options are required.")
    
    correct_count = sum(1 for o in options_data if o["is_correct"])

    if question_type == 'truefalse':
        if len(options_data) != 2:
            raise QuestionValidationError("True/False questions must have exactly two options.")
        if correct_count != 1:
            raise QuestionValidationError("True/False questions must have exactly one correct option.")
    
    elif question_type == 'single':
        if correct_count != 1:
            raise QuestionValidationError("Single-answer questions must have exactly one correct option.")
    
    elif question_type == 'multi':
        if correct_count < 1:
            raise QuestionValidationError("Multi-answer questions must have at least one correct option.")
        



