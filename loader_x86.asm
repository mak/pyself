;;;
;;;
;;; input list of 4-s
;;; 1) type: LOAD == 1 , STACK == 2 , ENTRYPOINT -- always last
;;; 2) vaddr
;;; 3) size -- page aligned?
;;; 4) data if type != ENTRYPOINT
;;;

;;;  syscalls numbers
%define SYS_MMAP 	  192
%define SYS_MUNMAP	  91
%define SYS_EXIT	  1

;;; mmap stuff - olac

;; %define PROT_READ	0x1		/* Page can be read.  */
;; %define PROT_WRITE	0x2		/* Page can be written.  */
;; %define PROT_EXEC	0x4		/* Page can be executed.  */

;; %define MAP_PRIVATE	0x02		/* Changes are private.  */
;; %define MAP_FIXED	0x10		/* Interpret addr exactly.  */
;; %define MAP_ANONYMOUS	0x20		/* Don't use a file.  */


;;;  paging stuff
%define PG_SIZE		0x1000
%define PG_MASK		0xfffff000
%macro mem_align 1

	add %1, PG_SIZE
	and %1, PG_MASK

%endmacro
;;;  my header stuff
%define LOAD_TYPE	1
%define	STACK_TYPE	2
%define	ENTRY_POINT	3

%define TYPE_OFF 	0
%define VADDR_OFF 	2
%define	SIZE_OFF	6
%define DATA_OFF	10

%define HDR_SIZE	10


	global loader
	section .text

loader:
	pop ebp			; ebp holds pointer to begin of my list

_load_next:

	mov eax,[ebp+TYPE_OFF]	; type -- only matter at begining
	test eax, LOAD_TYPE
	je _set_load
	test eax, STACK_TYPE
	je _set_stack
	test eax, ENTRY_POINT
	je _entryp
	;; die
	jmp _exit


_set_load:

	;; munmap region i dont care if its mmaped or not
	mov ebx, [ebp + VADDR_OFF]
	mov ecx, [ebp + SIZE_OFF]
	pusha
	mov eax,SYS_MUNMAP
	int 80h

	;; mmap region again -- always RWX?
	popa 			; vaddr and size are set
	push ebp		; mmap is scary i'd like to save my ptr on header
	mov edx, 7
	mov esi, 0x32
	mov edi, 0
	mov ebp, 0
	mov eax, SYS_MMAP
	int 80h

	;; copy stuff
	pop ebp
	lea esi, [ebp + DATA_OFF]
	mov edi, [ebp + VADDR_OFF]
	mov ecx, [ebp + SIZE_OFF ]
	repz movsb

	;; netx chunk
	lea eax, [ebp + HDR_SIZE]
	lea ebp, [eax + SIZE_OFF]
	jmp _load_next


_set_stack:			; just copy data, i dont give a shit

	lea esi, [ebp + DATA_OFF]
	mov edi, [ebp + VADDR_OFF]
	mov ecx, [ebp + SIZE_OFF ]
	repz movsb
	jmp _load_next

_entryp:
	mov eax,[ebp + SIZE_OFF]
	jmp eax

_exit:
	mov ebx,1
	mov eax,SYS_EXIT
	int 80h
