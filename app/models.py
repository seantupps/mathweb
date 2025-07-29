from django.db import models

class LeaderboardEntry(models.Model):
    operation = models.CharField(max_length=10)  # 'add', 'sub', 'mul', 'div'
    digits = models.IntegerField()  # 1-7
    num_questions = models.IntegerField()  # 3, 5, 10, 20, 40
    average_time = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['operation', 'digits', 'num_questions', 'average_time']),
        ]
    
    def __str__(self):
        return f"{self.operation} {self.digits}D {self.num_questions}Q - {self.average_time:.3f}s"