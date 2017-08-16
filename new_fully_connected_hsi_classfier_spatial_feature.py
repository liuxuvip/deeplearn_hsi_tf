
import tensorflow as tf
from new_SAE import new_SAE
import Config
from Data import Data
from Data import Data_Set
import time
import os.path
from Data import fill_feed_dict



def run_trainning():

    # # ## data 1------------------------
    #dataname = Config.paviaU
    # class_num =Config.paviaU_class_num
    # # ## data 1------------------------

    ## data 2------------------------
    # dataname = Config.ksc
    #class_num =Config.ksc_class_num
    ## data 2------------------------


    ## data 2------------------------
    dataname = Config.Salinas
    # class_num =Config.ksc_class_num
    ## data 2------------------------

    # log

    spatial_log='/'+dataname+'/'+'spatial'

    final_ckpt_dir=Config.final_ckpt_dir+spatial_log
    if not os.path.exists(final_ckpt_dir):
        os.makedirs(final_ckpt_dir)

    pre_train_ckpt_dir = Config.pretrain_ckpt+spatial_log

    if not os.path.exists(pre_train_ckpt_dir):
        os.makedirs(pre_train_ckpt_dir)

    pre_need_train = True
    final_need_train = True


    with tf.Graph().as_default() as gad:

        pd = Data(data_name = dataname)
        data_sets = pd.get_train_valid_test_of_spatial_feature()

        # init class
        train_data = Data_Set([data_sets[0],data_sets[1]])
        valid_data = Data_Set([data_sets[2],data_sets[3]])
        test_data = Data_Set([data_sets[4],data_sets[5]])

        with tf.Session(graph = gad) as sess:

            input_dim = [train_data.feature_dim,Config.batch_size]
            epoch_size = data_sets[0].shape[0]

            # int
            sae = new_SAE(input_dim, encoder_shape=Config.encoder_layers,
                          all_data_num=train_data._num_examples, transfer_function=tf.nn.sigmoid)
            pre_trian_saver = tf.train.Saver()  # after graph, sometime with variable name ,so so
            fianl_saver = tf.train.Saver()  # after graph, sometime with variable name ,so so

            writer = tf.summary.FileWriter(final_ckpt_dir,gad)
            init = tf.global_variables_initializer() # order is important,after graph
            sess.run(init)  #after graph

            # if pretrain ready
            if pre_need_train == True:
                path = os.path.join(pre_train_ckpt_dir,'SAE_graph')
                sae.pre_train(train_data,sess,path)
                pre_trian_saver.save(sess, os.path.join(pre_train_ckpt_dir, 'pre_train_model.ckpt'))

            else:
                ckpt = tf.train.get_checkpoint_state(pre_train_ckpt_dir)
                pre_trian_saver.restore(sess, ckpt.model_checkpoint_path)

            # train real model
            if final_need_train == True:
                for step in range(int(Config.epoch_final_train_times * epoch_size / Config.batch_size)):
                    start_time = time.time()
                    feed_dict = fill_feed_dict(train_data, sae.x, sae.y)

                    cost,_= sae.train_final_model(feed_dict,sess)

                    duration = time.time() - start_time

                    if step % 1000 == 0:
                        print('final model train : Step %d: loss = %.2f(%.3f sec)' % (step, cost, duration))
                        summary_ = sess.run(sae.final_merged, feed_dict=feed_dict)
                        writer.add_summary(summary_,step)
                        fianl_saver.save(sess, os.path.join(final_ckpt_dir, 'final_model.ckpt'))

                        precision = sess.run(sae.precision,
                                             feed_dict={sae.x: train_data._images,
                                                        sae.y: train_data._labels})
                        print(' Train data evaluation, precision=%f' % precision)

                        summary_p = sess.run(sae.precision_train_merged,
                                             feed_dict={sae.x: train_data._images,
                                                        sae.y: train_data._labels})
                        writer.add_summary(summary_p, step)

                    if (step + 1) % 1000 == 0 or (step + 1) == Config.max_steps:
                        print(' Valid data evaluation')
                        summary_p = sess.run(sae.precision_valid_merged,
                                             feed_dict={sae.x: valid_data._images,
                                                        sae.y: valid_data._labels})
                        writer.add_summary(summary_p, step)

                    if (step + 1) % 1000 == 0 or (step + 1) == Config.max_steps:
                        print(' Test data evaluation')
                        summary_p = sess.run(sae.precision_test_merged,
                                             feed_dict={sae.x: test_data._images,
                                                        sae.y: test_data._labels})
                        writer.add_summary(summary_p, step)

            else:

                ckpt = tf.train.get_checkpoint_state(final_ckpt_dir)
                fianl_saver.restore(sess, ckpt.model_checkpoint_path)
                # v = tf.get_collection(tf.GraphKeys.VARIABLES)

                # print(' Train data evaluation')
                # do_eval(sess,
                #         sae.correct,
                #         sae.x,
                #         sae.y,
                #         train_data)
                #
                # print(' Valid data evaluation')
                # do_eval(sess,
                #         sae.correct,
                #         sae.x,
                #         sae.y,
                #         valid_data)
                #
                # print(' Test data evaluation')
                # do_eval(sess,
                #         sae.correct,
                #         sae.x,
                #         sae.y,
                #         test_data)


if __name__ == "__main__":
    run_trainning()

    # get_result_from_log()