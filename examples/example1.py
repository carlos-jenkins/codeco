from codeco.processor import Processor


proc = Processor()
proc.create_document('source.py', 'annotations.md', out_file='test.html')
print('[DONE]')

