#include <stdio.h>
#include <string.h>

const char WILDCARD = 32;

const char* march(const char* a)
{
	for (unsigned cnt = 1; cnt; ++a)
	{
		if (!*a) return a;
		if (*a == '(') ++cnt;
		else if (*a == ')') --cnt;
	}
	return a-1;
}

int match(const char* a, const char* b)
{
	int flag = 0;
	for (; *a && *b && !flag;)
	{
		if (*a == WILDCARD)
		{
			if (*b == WILDCARD) ++b;
			else b = march(b);
			if (!*b) flag = 1;
			++a;
		} else
		{
			if (*b == WILDCARD)
			{
				a = march(a);
				if (!*a) flag = 2;
			}
			else
			{
				if (*a != *b) flag = 3;
				++a;
			}
			++b;
		}
	}
    if (*a && !*b) flag = 4;
	return flag;
}

int find(const char* a, const char* b)
{
	for (int cnt = 0; b[cnt]; ++cnt)
	{
		if (match(a,b+cnt) == 0)
			return cnt+1;
	}
	return -1;
}

