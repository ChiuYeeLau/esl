#include <cstdio>
#include <cstring>

const char WILDCARD = 32;
const int MLEN = 5000;

void march(const char*& a)
{
	for (unsigned cnt = 1; cnt; ++a)
	{
		if (!*a) return;
		if (*a == '(') ++cnt;
		else if (*a == ')') --cnt;
	}
	--a;
}

int match(const char* a, const char* b)
{
	int flag = 0;
	for (; *a && *b && !flag;)
	{
		if (*a == WILDCARD)
		{
			if (*b == WILDCARD) ++b;
			else march(b);
			if (!*b) flag = 1;
			++a;
		} else
		{
			if (*b == WILDCARD)
			{
				march(a);
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
	return flag;
}

const char* find(const char* a, const char* b)
{
	for (; *b; ++b)
	{
		if (!match(a,b))
			return b;
	}
	return nullptr;
}

char* getstr(char* str, FILE* fin)
{
	char* ret = fgets(str, MLEN, fin);
	if (ret)
	{
		int len = strlen(str);
		if (str[len-1] == '\n')
			str[len-1] = 0;
	}
	return ret;
}

int main(int argc, char** argv)
{
	FILE* finreq = fopen("./studio/request.txt", "r");
	FILE* findat = fopen("./studio/all.txt", "r");
	FILE* foutres = fopen("./studio/result.txt", "w");
	char pat[MLEN], tar[MLEN];
	getstr(pat, finreq);
	for (; getstr(tar, findat);)
	{
		if (find(pat, tar))
		{
			fputs(tar, foutres);
            fputc('\n', foutres);
		}
	}
	fclose(finreq);
	fclose(findat);
	fclose(foutres);
	return 0;
}
