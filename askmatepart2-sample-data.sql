--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.6
-- Dumped by pg_dump version 9.5.6

ALTER TABLE IF EXISTS ONLY public.question DROP CONSTRAINT IF EXISTS pk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS pk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS pk_comment_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS pk_question_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.tag DROP CONSTRAINT IF EXISTS pk_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS fk_tag_id CASCADE;

DROP TABLE IF EXISTS public.question;
DROP SEQUENCE IF EXISTS public.question_id_seq;
CREATE TABLE question (
    id serial NOT NULL,
    submission_time timestamp without time zone,
    view_number integer,
    vote_number integer,
    title text,
    message text,
    image text
);

DROP TABLE IF EXISTS public.answer;
DROP SEQUENCE IF EXISTS public.answer_id_seq;
CREATE TABLE answer (
    id serial NOT NULL,
    submission_time timestamp without time zone,
    vote_number integer,
    question_id integer,
    message text,
    image text
);

DROP TABLE IF EXISTS public.comment;
DROP SEQUENCE IF EXISTS public.comment_id_seq;
CREATE TABLE comment (
    id serial NOT NULL,
    question_id integer,
    answer_id integer,
    message text,
    submission_time timestamp without time zone
);


DROP TABLE IF EXISTS public.question_tag;
CREATE TABLE question_tag (
    question_id integer NOT NULL,
    tag_id integer NOT NULL
);

DROP TABLE IF EXISTS public.tag;
DROP SEQUENCE IF EXISTS public.tag_id_seq;
CREATE TABLE tag (
    id serial NOT NULL,
    name text
);


ALTER TABLE ONLY answer
    ADD CONSTRAINT pk_answer_id PRIMARY KEY (id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT pk_comment_id PRIMARY KEY (id);

ALTER TABLE ONLY question
    ADD CONSTRAINT pk_question_id PRIMARY KEY (id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT pk_question_tag_id PRIMARY KEY (question_id, tag_id);

ALTER TABLE ONLY tag
    ADD CONSTRAINT pk_tag_id PRIMARY KEY (id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_answer_id FOREIGN KEY (answer_id) REFERENCES answer(id);

ALTER TABLE ONLY answer
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_tag_id FOREIGN KEY (tag_id) REFERENCES tag(id);

INSERT INTO question VALUES (0, '2017-04-28 08:29:00', 29, 7, 'SG93IHRvIG1ha2UgbGlzdHMgaW4gUHl0aG9uPw==', 'SSBhbSB0b3RhbGx5IG5ldyB0byB0aGlzLCBhbnkgaGludHM/', NULL);
INSERT INTO question VALUES (1, '2017-04-29 09:19:00', 15, 9, 'V29yZHByZXNzIGxvYWRpbmcgbXVsdGlwbGUgalF1ZXJ5IFZlcnNpb25z', 'SSBkZXZlbG9wZWQgYSBwbHVnaW4gdGhhdCB1c2VzIHRoZSBqcXVlcnkgYm9va2xldCBwbHVnaW4gKGh0dHA6Ly9idWlsdGJ5d2lsbC5jb20vYm9va2xldC8jLykgdGhpcyBwbHVnaW4gYmluZHMgYSBmdW5jdGlvbiB0byAkIHNvIEkgY2FubiBjYWxsICQoIi5teUJvb2siKS5ib29rbGV0KCk7CgpJIGNvdWxkIGVhc3kgbWFuYWdpbmcgdGhlIGxvYWRpbmcgb3JkZXIgd2l0aCB3cF9lbnF1ZXVlX3NjcmlwdCBzbyBmaXJzdCBJIGxvYWQganF1ZXJ5IHRoZW4gSSBsb2FkIGJvb2tsZXQgc28gZXZlcnl0aGluZyBpcyBmaW5lLgoKQlVUIGluIG15IHRoZW1lIGkgYWxzbyB1c2luZyBqcXVlcnkgdmlhIHdlYnBhY2sgc28gdGhlIGxvYWRpbmcgb3JkZXIgaXMgbm93IGZvbGxvd2luZzoKCmpxdWVyeQpib29rbGV0CmFwcC5qcyAoYnVuZGxlZCBmaWxlIHdpdGggd2VicGFjaywgaW5jbHVkaW5nIGpxdWVyeSk=', 'aW1hZ2VzL2ltYWdlMS5wbmc=');
INSERT INTO question VALUES (2, '2017-05-01 10:41:00', 1364, 57, 'RHJhd2luZyBjYW52YXMgd2l0aCBhbiBpbWFnZSBwaWNrZWQgd2l0aCBDb3Jkb3ZhIENhbWVyYSBQbHVnaW4=', 'SSdtIGdldHRpbmcgYW4gaW1hZ2UgZnJvbSBkZXZpY2UgYW5kIGRyYXdpbmcgYSBjYW52YXMgd2l0aCBmaWx0ZXJzIHVzaW5nIFBpeGkgSlMuIEl0IHdvcmtzIGFsbCB3ZWxsIHVzaW5nIGNvbXB1dGVyIHRvIGdldCBhbiBpbWFnZS4gQnV0IHdoZW4gSSdtIG9uIElPUywgaXQgdGhyb3dzIGVycm9ycyBzdWNoIGFzIGNyb3NzIG9yaWdpbiBpc3N1ZSwgb3IgdGhhdCBJJ20gdHJ5aW5nIHRvIHVzZSBhbiB1bmtub3duIGZvcm1hdC4KClRoaXMgaXMgdGhlIGNvZGUgSSdtIHVzaW5nIHRvIGRyYXcgdGhlIGltYWdlICh0aGF0IHdvcmtzIG9uIHdlYi9kZXNrdG9wIGJ1dCBub3QgY29yZG92YSBidWlsdCBpb3MgYXBwKQ=SSdtIGdldHRpbmcgYW4gaW1hZ2UgZnJvbSBkZXZpY2UgYW5kIGRyYXdpbmcgYSBjYW52YXMgd2l0aCBmaWx0ZXJzIHVzaW5nIFBpeGkgSlMuIEl0IHdvcmtzIGFsbCB3ZWxsIHVzaW5nIGNvbXB1dGVyIHRvIGdldCBhbiBpbWFnZS4gQnV0IHdoZW4gSSdtIG9uIElPUywgaXQgdGhyb3dzIGVycm9ycyBzdWNoIGFzIGNyb3NzIG9yaWdpbiBpc3N1ZSwgb3IgdGhhdCBJJ20gdHJ5aW5nIHRvIHVzZSBhbiB1bmtub3duIGZvcm1hdC4KClRoaXMgaXMgdGhlIGNvZGUgSSdtIHVzaW5nIHRvIGRyYXcgdGhlIGltYWdlICh0aGF0IHdvcmtzIG9uIHdlYi9kZXNrdG9wIGJ1dCBub3QgY29yZG92YSBidWlsdCBpb3MgYXBwKQ=', NULL);
SELECT pg_catalog.setval('question_id_seq', 2, true);

INSERT INTO answer VALUES (1, '2017-04-28 16:49:00', 4, 1, 'WW91IG5lZWQgdG8gdXNlIGJyYWNrZXRzOiBteV9saXN0ID0gW10=', NULL);
INSERT INTO answer VALUES (2, '2017-04-25 14:42:00', 35, 1, 'TG9vayBpdCB1cCBpbiB0aGUgUHl0aG9uIGRvY3M=', 'aW1hZ2VzL2ltYWdlMi5qcGc=');
SELECT pg_catalog.setval('answer_id_seq', 2, true);

INSERT INTO comment VALUES (1, 0, NULL, 'UGxlYXNlIGNsYXJpZnkgdGhlIHF1ZXN0aW9uIGFzIGl0IGlzIHRvbyB2YWd1ZSE=', '2017-05-01 05:49:00');
INSERT INTO comment VALUES (2, NULL, 1, 'SSB0aGluayB5b3UgY291bGQgdXNlIG15X2xpc3QgPSBsaXN0KCkgYXMgd2VsbC4=', '2017-05-02 16:55:00');
SELECT pg_catalog.setval('comment_id_seq', 2, true);

INSERT INTO tag VALUES (1, 'cHl0aG9u');
INSERT INTO tag VALUES (2, 'c3Fs');
INSERT INTO tag VALUES (3, 'Y3Nz');
SELECT pg_catalog.setval('tag_id_seq', 3, true);

INSERT INTO question_tag VALUES (0, 1);
INSERT INTO question_tag VALUES (1, 3);
INSERT INTO question_tag VALUES (2, 3);