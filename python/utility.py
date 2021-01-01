def log_print(s:str) -> str:
   if s:
      if (len(s) <= 120):
         return s
      else:
         return s[0:120] + '...'
   else:
      return s 
