
import tensorflow as tf
import sAE
import time
import Config
from Data import Data
from Data import Data_Set
import numpy as np

import os.path

def placeholder_inputs(batch_size=Config.batch_size,input_dim=0):

    # define input
    images_placeholder = tf.placeholder(tf.float32,shape=(batch_size,input_dim))

    #define output
    labels_placeholder = tf.placeholder(tf.int32,shape=(batch_size))

    return images_placeholder,labels_placeholder


def fill_feed_dict(data_set,images_pl,labels_pl):

    images_feed,labels_feed = data_set.next_batch(Config.batch_size)

    feed_dict={images_pl:images_feed,labels_pl:labels_feed}

    return feed_dict

def do_eval(sess,
            eval_correct,
            images_placeholder,
            labels_placeholder,
            data_set
            ):

    true_count= 0

    steps_per_epoch = data_set._num_examples // Config.batch_size
    num_examples = steps_per_epoch*Config.batch_size

    for step in range(steps_per_epoch):

        feed_dict = fill_feed_dict(data_set, images_placeholder, labels_placeholder)
        true_count += sess.run(eval_correct,feed_dict=feed_dict)


    #print(true_count,true_count.shape)
    #aa = np.sum(true_count)

    precision = float(true_count)/num_examples
    print('NUm examples:%d Num correct:%d Precision @1:%0.04f' %(num_examples,true_count,precision))


def run_trainning():


# ## data 1------------------------
    dataname = Config.paviaU
    class_num =Config.paviaU_class_num
# ## data 1------------------------


## data 2------------------------
    # dataname = Config.ksc
    # class_num =Config.ksc_class_num
## data 2------------------------


    #set log dir
    log = './'+dataname+'/'+Config.spatial_log

    with tf.Graph().as_default():

        pd = Data(dataname)
        data_sets = pd.get_train_valid_test_of_spatial_feature()

        # init class
        train_data = Data_Set([data_sets[0],data_sets[1]])
        valid_data = Data_Set([data_sets[2],data_sets[3]])
        test_data = Data_Set([data_sets[4],data_sets[5]])

        images_placeholder, labels_placeholder = \
            placeholder_inputs(input_dim=data_sets[0].shape[1])

        logits = sAE.inference(images_placeholder,class_num,Config.encoder_layers)
        loss = sAE.loss(logits,labels_placeholder)

        loss_summary = tf.summary.scalar('loss',loss)

        train_op = sAE.training(loss,Config.learn_rate)
        eval_correct = sAE.evaluation(logits,labels_placeholder)

        summary = tf.summary.merge_all()

        saver = tf.train.Saver()
        sess = tf.Session()
        summary_writer = tf.summary.FileWriter(log,sess.graph)


        init = tf.global_variables_initializer()
        sess.run(init)

        for step in range(105):
            start_time = time.time()
            feed_dict = fill_feed_dict(train_data,images_placeholder,labels_placeholder)
            # only return loss inside run([])
            _,loss_value = sess.run([train_op,loss],feed_dict=feed_dict)
            duration = time.time()-start_time

            if step%100 == 0:
                print('Step %d: loss = %.2f(%.3f sec)'%(step,loss_value,duration))
                #print(sess.run(sAE.evaluation(logits, train_data[1])))

                summary_str = sess.run(summary,feed_dict=feed_dict)
                summary_writer.add_summary(summary_str,step)
                #summary_writer.flush()

            if(step+1)%100 == 0 or (step+1)==Config.max_steps:
                checkpoint_file = log+'/valid/valid_model.ckpt'
                saver.save(sess,checkpoint_file,global_step = step)
                print(' Valid data evaluation')
                do_eval(sess,
                        eval_correct,
                        images_placeholder,
                        labels_placeholder,
                        valid_data)

            if (step + 1) % 100 == 0 or (step + 1) == Config.max_steps:
                checkpoint_file = log+'/test/test_model.ckpt'
                saver.save(sess, checkpoint_file, global_step=step)
                print(' Test data evaluation')
                do_eval(sess,
                        eval_correct,
                        images_placeholder,
                        labels_placeholder,
                        test_data)

def get_results_from_exist_model():
    # ## data 2------------------------
    dataname = Config.paviaU
    class_num = Config.paviaU_class_num
    # ## data 2------------------------

    # ## data 2------------------------
    # dataname = Config.ksc
    # class_num =Config.ksc_class_num
    # ## data 2------------------------

    #set log dir
    log = './'+dataname+'/'+Config.spatial_log

    with tf.Graph().as_default():

        pd = Data(data_name=dataname)
        data_sets = pd.get_train_valid_test_of_spatial_feature()

        # init class
        train_data = Data_Set([data_sets[0], data_sets[1]])
        valid_data = Data_Set([data_sets[2], data_sets[3]])
        test_data = Data_Set([data_sets[4], data_sets[5]])

        images_placeholder, labels_placeholder = \
            placeholder_inputs(input_dim=data_sets[0].shape[1])

        logits = sAE.inference(images_placeholder, class_num, Config.encoder_layers)

        loss = sAE.loss(logits, labels_placeholder)

        train_op = sAE.training(loss, Config.learn_rate)

        eval_correct = sAE.evaluation(logits, labels_placeholder)



        saver = tf.train.Saver()

        # valid_saver = tf.train.Saver()
        # test_saver = tf.train.Saver()

        with tf.Session() as sess:

            sess.run(tf.global_variables_initializer())
            path = log+'/test/test_model.ckpt-99'
            model_file = tf.train.latest_checkpoint(log+'/test')
            saver.restore(sess, model_file)


            print('success')
            for step in range(Config.max_steps):

                feed_dict = fill_feed_dict(train_data,images_placeholder,labels_placeholder)
                # only return loss inside run([])
                _,loss_value = sess.run([train_op,loss],feed_dict=feed_dict)

                if (step + 1) % 100 == 0 or (step + 1) == Config.max_steps:
                    # checkpoint_file = os.path.join(log, 'valid_model.ckpt')
                    # valid_saver.restore(sess, checkpoint_file)
                    # #saver.save(sess, checkpoint_file, global_step=step)
                    print(' Valid data evaluation')

                    do_eval(sess,
                            eval_correct,
                            images_placeholder,
                            labels_placeholder,
                            valid_data)

                if (step + 1) % 100 == 0 or (step + 1) == Config.max_steps:
                    # checkpoint_file1 = os.path.join(log, 'test_model.ckpt')
                    # test_saver.restore(sess, checkpoint_file1)
                    # # tf.saver.save(sess, checkpoint_file, global_step=step)
                    print(' Test data evaluation')

                    do_eval(sess,
                            eval_correct,
                            images_placeholder,
                            labels_placeholder,
                            test_data)

if __name__ == "__main__":

    run_trainning()
    get_results_from_exist_model()
