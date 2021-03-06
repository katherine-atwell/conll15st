import json
import sys
from scorer import evaluate
from validator import validate_relation_list

def write_proto_text(key, value, f):
	f.write('measure {\n key: "%s" \n value: "%s"\n}\n' % (key ,round(value, 4)))

def write_results(prefix, result_tuple, output_file):
	connective_cm, arg1_cm, arg2_cm, rel_arg_cm, sense_cm, precision, recall, f1 = result_tuple
	write_proto_text('%s Parser precision' % prefix, precision, output_file)
	write_proto_text('%s Parser recall' % prefix, recall, output_file)
	write_proto_text('%s Parser f1' % prefix, f1, output_file)

	p, r, f = connective_cm.get_prf('yes')
	write_proto_text('%s Explicit connective precision' % prefix, p, output_file)
	write_proto_text('%s Explicit connective recall' % prefix, r, output_file)
	write_proto_text('%s Explicit connective f1' % prefix, f, output_file)

	p, r, f = arg1_cm.get_prf('yes')
	write_proto_text('%s Arg1 extraction precision' % prefix, p, output_file)
	write_proto_text('%s Arg1 extraction recall' % prefix, r, output_file)
	write_proto_text('%s Arg1 extraction f1' % prefix, f, output_file)

	p, r, f = arg2_cm.get_prf('yes')
	write_proto_text('%s Arg2 extraction precision' % prefix, p, output_file)
	write_proto_text('%s Arg2 extraction recall' % prefix, r, output_file)
	write_proto_text('%s Arg2 extraction f1' % prefix, f, output_file)

	p, r, f = rel_arg_cm.get_prf('yes')
	write_proto_text('%s Arg 1 Arg2 extraction precision' % prefix, p, output_file)
	write_proto_text('%s Arg 1 Arg2 extraction recall' % prefix, r, output_file)
	write_proto_text('%s Arg 1 Arg2 extraction f1' % prefix, f, output_file)

	p, r, f = sense_cm.compute_average_prf()
	write_proto_text('%s Sense precision' % prefix, p, output_file)
	write_proto_text('%s Sense recall' % prefix, r, output_file)
	write_proto_text('%s Sense f1' % prefix, f, output_file)

if __name__ == '__main__':
	input_dataset = sys.argv[1]
	input_run = sys.argv[2]
	output_dir = sys.argv[3]

	gold_relations = [json.loads(x) for x in open('%s/pdtb-data.json' % input_dataset)]
	predicted_relations = [json.loads(x) for x in open('%s/output.json' % input_run)]
	all_correct = validate_relation_list(predicted_relations)
	if not all_correct:
		exit(1)

	output_file = open('%s/evaluation.prototext' % output_dir, 'w')
	print 'Evaluation for all discourse relations'
	write_results('All', evaluate(gold_relations, predicted_relations), output_file)

	print 'Evaluation for explicit discourse relations only'
	explicit_gold_relations = [x for x in gold_relations if x['Type'] == 'Explicit']
	explicit_predicted_relations = [x for x in predicted_relations if x['Type'] == 'Explicit']
	write_results('Explicit only', evaluate(explicit_gold_relations, explicit_predicted_relations), output_file)

	print 'Evaluation for non-explicit discourse relations only (Implicit, EntRel, AltLex)'
	non_explicit_gold_relations = [x for x in gold_relations if x['Type'] != 'Explicit']
	non_explicit_predicted_relations = [x for x in predicted_relations if x['Type'] != 'Explicit']
	write_results('Non-explicit only', evaluate(non_explicit_gold_relations, non_explicit_predicted_relations), output_file)
	
	output_file.close()

