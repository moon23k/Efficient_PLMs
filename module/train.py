import numpy as np
import torch, evaluate
from transformers import (
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding    
)





def set_trainer(config, model, tokenizer, train_dataset, valid_dataset):

    training_args = TrainingArguments(
        
        output_dir= config.ckpt,
        num_train_epochs= config.n_epochs,
        learning_rate= config.lr,
        per_device_train_batch_size= config.batch_size,
        per_device_eval_batch_size= config.batch_size,
        lr_scheduler_type='reduce_lr_on_plateau',
        load_best_model_at_end= True,

        save_strategy= 'epoch',
        logging_strategy= 'epoch',
        evaluation_strategy= 'epoch',

        fp16= config.task == 'imdb',
        fp16_opt_level= '02' if config.task == 'imdb' else '01',
        gradient_accumulation_steps = 4,
        gradient_checkpointing = config.task == 'imdb',
        optim = 'adafactor'
    )


    accuracy = evaluate.load("accuracy")
    def compute_metrics(eval_pred):
        
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        return accuracy.compute(predictions=predictions, references=labels)


    trainer = Trainer(
        model=model, 
        args=training_args, 
        train_dataset=train_dataset, 
        eval_dataset=valid_dataset,
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics
    )


    return trainer
