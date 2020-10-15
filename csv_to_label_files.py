import csv
import os

with open('/Users/crystal.butler/Desktop/IPD/video_labels.csv', newline='') as csvfile:
    video_id = 0000
    videos = csv.reader(csvfile, delimiter=',')
    for row in videos:
        next_id = row[0]
        if next_id != video_id:
            video_id = next_id
            out_file = os.path.join('/Users/crystal.butler/Desktop/IPD/Label_Lists', video_id + '.txt')
            f_out = open(out_file, 'w')
        f_out.write("%s\n" % (row[1]))
    f_out.close()
