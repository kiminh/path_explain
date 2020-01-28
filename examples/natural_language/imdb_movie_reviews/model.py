import tensorflow as tf
from path_explain.utils import softplus_activation

def lstm_model(vocab_length,
               embedding_dim=32,
               sequence_length=400,
               dropout_rate=0.5,
               lstm_units=32,
               hidden_units=20,
               for_interpretation=False):
    input_shape = (sequence_length,)
    activation_function = tf.keras.activations.relu
    if for_interpretation:
        activation_function = softplus_activation(beta=10.0)

    model = tf.keras.models.Sequential()

    if not for_interpretation:
        model.add(tf.keras.layers.Input(shape=input_shape, name='input'))
        model.add(tf.keras.layers.Embedding(vocab_length,
                                            embedding_dim,
                                            input_length=sequence_length,
                                            name="embedding"))

    else:
         model.add(tf.keras.layers.Input(shape=(sequence_length, embedding_dim),
                                            name='input'))

    model.add(tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(units=lstm_units,
                                                                 return_sequences=True,
                                                                 name='lstm'),
                                            name='bidirectional'))
    model.add(tf.keras.layers.GlobalMaxPool1D(name='pool'))
    model.add(tf.keras.layers.Dense(units=hidden_units,
                                    activation=activation_function,
                                    name='dense'))
    model.add(tf.keras.layers.Dropout(dropout_rate,
                                      name='dropout'))
    model.add(tf.keras.layers.Dense(1,
                                    activation=None,
                                    name='dense_out'))
    if not for_interpretation:
        model.add(tf.keras.layers.Activation(activation=tf.keras.activations.sigmoid,
                                             name='sigmoid'))
    return model

def cnn_model(vocab_length,
              embedding_dim=32,
              sequence_length=400,
              dropout_rate=0.5,
              num_filters=32,
              hidden_units=50,
              for_interpretation=False):
    input_shape = (sequence_length,)
    activation_function = tf.keras.activations.relu
    if for_interpretation:
        activation_function = softplus_activation(beta=10.0)

    if not for_interpretation:
        model_input = tf.keras.layers.Input(shape=input_shape,
                                            name='input')
        embedding_layer = tf.keras.layers.Embedding(vocab_length,
                                                    embedding_dim,
                                                    input_length=sequence_length,
                                                    name="embedding")(model_input)
        dropout_layer = tf.keras.layers.Dropout(rate=dropout_rate,
                                                name="embedding_dropout")(embedding_layer)
    else:
        model_input = tf.keras.layers.Input(shape=(sequence_length, embedding_dim),
                                            name='input')
        dropout_layer = model_input

    conv_blocks = []
    filter_sizes = (3, 8)
    for filter_size in filter_sizes:
        conv = tf.keras.layers.Conv1D(filters=num_filters,
                                      kernel_size=filter_size,
                                      padding="valid",
                                      activation=activation_function,
                                      strides=1,
                                      name='conv_{}'.format(filter_size))(dropout_layer)
        conv = tf.keras.layers.MaxPooling1D(pool_size=2,
                                            name='pool_{}'.format(filter_size))(conv)
        conv = tf.keras.layers.Flatten(name='flatten_{}'.format(filter_size))(conv)
        conv_blocks.append(conv)
    conv_output = tf.keras.layers.Concatenate(name='concat_conv')(conv_blocks)

    second_dropout_layer = tf.keras.layers.Dropout(rate=dropout_rate, name='dropout_conv')(conv_output)
    dense_layer = tf.keras.layers.Dense(hidden_units,
                                        activation=activation_function,
                                        name='dense')(second_dropout_layer)
    dense_output = tf.keras.layers.Dense(1,
                                         activation=None,
                                         name='dense_out')(dense_layer)

    if not for_interpretation:
        dense_output = tf.keras.layers.Activation(activation=tf.keras.activations.sigmoid,
                                                  name='sigmoid')(dense_output)

    model = tf.keras.models.Model(model_input, dense_output)
    return model
